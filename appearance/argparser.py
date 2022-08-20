"""Module which encompasses console arguments settings and parsing logics."""
import argparse


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
            version="0.0.1",
        )
        self.parser.add_argument(
            "--verbose", help="Output verbose status messages.", action="store_true"
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
            action='store_true'
        )
        self.parser.add_argument(
            "-r",
            "--restore",
            help="Restore characters file from backup.",
            metavar='RESTORE_FROM'
        )
        self.parser.add_argument(
            "-g",
            "--gen",
            help="Generate N random characters.",
            metavar='N',
            type=int
        )

    @property
    def args(self) -> argparse.Namespace:
        """Property field to return parsed console arguments."""
        return self.parser.parse_args()
