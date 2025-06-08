import logging
from pathlib import Path

from appearance.argparser import ArgParser
from appearance.consts import BACKUP_FILE_DIR, RESOURCES_FILE_DIR, get_profiles_file_path
from appearance.service import backup, delete_character, generate_n_random_characters, list_characters, restore_from_backup, show_backuped_characters
from appearance.validators import validate_file_exists


def main():
    arg_parser = ArgParser()
    cli_args = arg_parser.args

    # Configure logging based on CLI flags
    if cli_args.quiet:
        log_level = logging.ERROR
    elif cli_args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s"
    )

    backup_to: str = cli_args.backup
    show_backups: bool = cli_args.show
    restore_from: str = cli_args.restore
    generate: int = cli_args.gen
    delete: str = cli_args.delete
    list_chars: bool = cli_args.list
    wse2: bool = cli_args.wse2
    show_face_codes: bool = cli_args.show_face_codes

    if not (backup_to or restore_from or generate or show_backups or delete or list_chars):
        arg_parser.parser.error("No action requested!")

    if show_backups:
        show_backuped_characters(BACKUP_FILE_DIR)

    if backup_to:
        if not backup_to.endswith(".dat"):
            backup_to = backup_to.split(".")[0] + ".dat"
        backup(backup_to, wse2)

    if restore_from:
        if not restore_from.endswith(".dat"):
            restore_from = restore_from.split(".")[0] + ".dat"
        if validate_file_exists(Path(BACKUP_FILE_DIR, restore_from)):
            restore_from_backup(BACKUP_FILE_DIR, restore_from, wse2)
        elif validate_file_exists(Path(RESOURCES_FILE_DIR, restore_from)):
            restore_from_backup(RESOURCES_FILE_DIR, restore_from, wse2)
        else:
            arg_parser.parser.error("Malformed restore path!")

    if generate:
        generate_n_random_characters(generate, wse2)
    
    if delete:
        profiles_path = get_profiles_file_path(wse2)
        # Try to parse as integer (index)
        try:
            index = int(delete)
            success = delete_character(str(profiles_path), index=index)
        except ValueError:
            # It's a name
            success = delete_character(str(profiles_path), name=delete)
        
        if not success:
            arg_parser.parser.error("Failed to delete character!")
    
    if list_chars:
        profiles_path = get_profiles_file_path(wse2)
        characters = list_characters(wse2=wse2)
        if not characters:
            logging.info("No characters found or unable to read %s.", profiles_path)
        else:
            logging.info("Characters in %s:", profiles_path)
            for char in characters:
                # Build character info string with available properties
                info_parts = [char['sex'], char['skin']]
                
                if 'age' in char:
                    info_parts.append(f"Age:{char['age']}")
                
                if 'hairstyle' in char:
                    info_parts.append(f"Hair:{char['hairstyle']}")
                
                if 'hair_color' in char:
                    info_parts.append(f"HairColor:{char['hair_color']}")
                
                if 'banner' in char:
                    info_parts.append(f"Banner:{char['banner']}")
                
                info_str = ", ".join(info_parts)
                
                # Add face code if requested
                if show_face_codes and 'face_code' in char and char['face_code']:
                    logging.info(f"{char['index'] + 1}. {char['name']} ({info_str})")
                    logging.info(f"   Face Code: {char['face_code']}")
                else:
                    logging.info(f"{char['index'] + 1}. {char['name']} ({info_str})")
