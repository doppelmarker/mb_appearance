from pathlib import Path

from appearance.argparser import ArgParser
from appearance.consts import BACKUP_FILE_DIR, RESOURCES_FILE_DIR
from appearance.service import backup, restore_from_backup, generate_n_random_characters, show_backuped_characters
from appearance.validators import validate_file_exists


def main():
    arg_parser = ArgParser()
    cli_args = arg_parser.args

    backup_to: str = cli_args.backup
    show_backups: bool = cli_args.show
    restore_from: str = cli_args.restore
    generate: int = cli_args.gen
    wse2: bool = cli_args.wse2

    if not (backup_to or restore_from or generate or show_backups):
        arg_parser.parser.error('No action requested!')

    if show_backups:
        show_backuped_characters(BACKUP_FILE_DIR)

    if backup_to:
        if not backup_to.endswith('.dat'):
            backup_to = backup_to.split('.')[0] + '.dat'
        backup(backup_to, wse2)

    if restore_from:
        if not restore_from.endswith('.dat'):
            restore_from = restore_from.split('.')[0] + '.dat'
        if validate_file_exists(Path(BACKUP_FILE_DIR, restore_from)):
            restore_from_backup(BACKUP_FILE_DIR, restore_from, wse2)
        elif validate_file_exists(Path(RESOURCES_FILE_DIR, restore_from)):
            restore_from_backup(RESOURCES_FILE_DIR, restore_from, wse2)
        else:
            arg_parser.parser.error('Malformed restore path!')

    if generate:
        generate_n_random_characters(generate, wse2)
