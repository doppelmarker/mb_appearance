from pathlib import Path

from appearance.argparser import ArgParser
from appearance.consts import BACKUP_FILE_DIR, RESOURCES_FILE_DIR
from appearance.service import backup, restore_from_backup, generate_n_random_characters
from appearance.validators import validate_file_exists


def main():
    arg_parser = ArgParser()
    cli_args = arg_parser.args

    backup_to: str = cli_args.backup
    restore_from: str = cli_args.restore
    generate: int = cli_args.gen

    if not (backup_to or restore_from or generate):
        arg_parser.parser.error('No action requested!')

    if backup_to:
        if not backup_to.endswith('.dat'):
            backup_to = backup_to.split('.')[0] + '.dat'
        backup(backup_to)

    if restore_from:
        if not restore_from.endswith('.dat'):
            restore_from = restore_from.split('.')[0] + '.dat'
        if validate_file_exists(Path(BACKUP_FILE_DIR, restore_from)):
            restore_from_backup(BACKUP_FILE_DIR, restore_from)
        elif validate_file_exists(Path(RESOURCES_FILE_DIR, restore_from)):
            restore_from_backup(RESOURCES_FILE_DIR, restore_from)
        else:
            arg_parser.parser.error('Malformed restore path!')

    if generate:
        generate_n_random_characters(generate)
