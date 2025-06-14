"""Module which encompasses console arguments settings and parsing logics."""
import argparse

from .__version__ import __version__


class ArgParser:
    """Class parsing console arguments."""

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog="mb-app",
            description="Python util for Mount&Blade characters file manipulation.",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog, max_help_position=48
            ),
            add_help=False,
        )
        self.parser.add_argument(
            "-h",
            "--help",
            action="help",
            default=argparse.SUPPRESS,
            help="Show this help message and exit.",
        )
        self.parser.add_argument(
            "-v",
            "--version",
            help="Print version info.",
            action="version",
            version=__version__,
        )
        self.parser.add_argument(
            "--verbose", help="Output verbose status messages.", action="store_true"
        )
        self.parser.add_argument(
            "--quiet", help="Suppress all output except errors.", action="store_true"
        )
        self.parser.add_argument(
            "-l",
            "--list",
            help="List all characters.",
            action="store_true"
        )
        self.parser.add_argument(
            "--show-face-codes",
            help="Show face codes when listing characters.",
            action="store_true"
        )
        self.parser.add_argument(
            "-g",
            "--gen",
            help="Generate N random characters.",
            metavar="N",
            type=int
        )
        self.parser.add_argument(
            "-d",
            "--delete",
            help="Delete a character by index or name.",
            metavar="INDEX_OR_NAME"
        )
        self.parser.add_argument(
            "-b",
            "--backup",
            help="Backup characters file.",
            metavar="BACKUP_TO"
        )
        self.parser.add_argument(
            "-s",
            "--show",
            help="Show backuped characters.",
            action="store_true"
        )
        self.parser.add_argument(
            "-r",
            "--restore",
            help="Restore characters file from backup.",
            metavar="RESTORE_FROM"
        )
        self.parser.add_argument(
            "--wse2",
            help="Use WSE2 (Warband Script Enhancer 2) profiles directory.",
            action="store_true"
        )

    @property
    def args(self) -> argparse.Namespace:
        """Property field to return parsed console arguments."""
        return self.parser.parse_args()
