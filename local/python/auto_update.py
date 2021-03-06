"""
auto_update.py
"""
import argparse
import config
import pathlib
import shutil
import sys
import modules.run_shell_cmds as rsc

auto_update_version = "0.3.0"


def get_cmdline_args():
    parser = argparse.ArgumentParser(description="auto_update")

    parser.add_argument(
        "-a", "--application", required=True,
        help="""Application - The name of the application being
        updated. Must match the name know to GIT."""

    )

    parser.add_argument(
        "-e", "--environment", required=True,
        choices=['devl', 'test', 'prod'],
        help="Environment - devl, test, or prod"
    )

    args = parser.parse_args()
    return args


def process_asset(environment, cfg, asset):
    home = str(pathlib.Path.home())
    src_dir = cfg[f'{environment}.{asset}_assets.src_dir']
    trg_dir = home + cfg[f'{environment}.{asset}_assets.trg_dir']
    file_names = cfg[f'{environment}.{asset}_assets.file_names']
    file_mode = cfg[f'{environment}.{asset}_assets.file_mode']

    print(f'\n  Updating {asset} assets...')
    print(f'    Copying from {src_dir} to {trg_dir}')

    #  Test that the directories exists
    if not pathlib.Path(src_dir).is_dir():
        print(f'      Error!  The source directory "{src_dir}" \
does not exist!')
        return

    if not pathlib.Path(trg_dir).is_dir():
        print('The target directory "{}" does not exist!'.format(trg_dir))
        return

    copy_files(src_dir, trg_dir, file_names, file_mode)


def copy_files(source_dir, target_dir, file_names, file_mode):
    for file in file_names:
        source_file = source_dir + "/" + file
        target_file = target_dir + "/" + file

        msg = f'      {file}'

        try:
            shutil.copyfile(source_file, target_file)
        except FileNotFoundError:
            msg += ' - was not found in the source directory.'
            print(msg)
            continue

#         os.chmod(target_file, file_mode)
        print(f'{msg} successful.')


def main():
    args = get_cmdline_args()
    application_name = args.application
    environment = args.environment

    cmd = f"cd /tmp ; git clone https://github.com/jasmit35/{application_name}.git"
    rc, stdout, stderr = rsc.run_shell_cmds(cmd)
    sys.stdout.buffer.write(stdout)
    if rc:
        sys.stderr.buffer.write(stderr)
        sys.exit(rc)

    if environment == 'devl':
        print("Processing complete for development environment.")
        sys.exit(0)

    cfg = config.Config(
        f'/tmp/{application_name}/{application_name}_au.cfg'
    )
    assets = cfg[f'{environment}.assets']
    for asset in assets:
        process_asset(environment, cfg, asset)

    sys.exit(0)


if __name__ == "__main__":
    main()
