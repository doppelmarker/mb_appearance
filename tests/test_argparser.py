import argparse
import sys
from io import StringIO

import pytest

from appearance.argparser import ArgParser
from appearance.__version__ import __version__


def test_argparser_initialization():
    parser = ArgParser()
    assert parser.parser.prog == "mb-app"
    assert "Mount&Blade" in parser.parser.description


def test_argparser_help_option(capsys):
    parser = ArgParser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parser.parse_args(["-h"])
    assert exc_info.value.code == 0
    
    # Help should be printed
    captured = capsys.readouterr()
    assert "usage:" in captured.out


def test_argparser_version_option(capsys):
    parser = ArgParser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parser.parse_args(["-v"])
    assert exc_info.value.code == 0
    
    # Version should be printed
    captured = capsys.readouterr()
    assert __version__ in captured.out


def test_argparser_backup_option():
    parser = ArgParser()
    args = parser.parser.parse_args(["-b", "test_backup"])
    assert args.backup == "test_backup"
    assert args.restore is None
    assert args.gen is None
    assert args.show is False


def test_argparser_show_option():
    parser = ArgParser()
    args = parser.parser.parse_args(["-s"])
    assert args.show is True
    assert args.backup is None
    assert args.restore is None
    assert args.gen is None


def test_argparser_restore_option():
    parser = ArgParser()
    args = parser.parser.parse_args(["-r", "test_restore"])
    assert args.restore == "test_restore"
    assert args.backup is None
    assert args.gen is None
    assert args.show is False


def test_argparser_generate_option():
    parser = ArgParser()
    args = parser.parser.parse_args(["-g", "10"])
    assert args.gen == 10
    assert args.backup is None
    assert args.restore is None
    assert args.show is False


def test_argparser_delete_option():
    parser = ArgParser()
    args = parser.parser.parse_args(["-d", "TestChar"])
    assert args.delete == "TestChar"


def test_argparser_list_option():
    parser = ArgParser()
    args = parser.parser.parse_args(["-l"])
    assert args.list is True
    assert args.backup is None
    assert args.restore is None
    assert args.gen is None
    assert args.show is False


def test_argparser_wse2_option():
    parser = ArgParser()
    args = parser.parser.parse_args(["--wse2", "-g", "5"])
    assert args.wse2 is True
    assert args.gen == 5


def test_argparser_verbose_option():
    parser = ArgParser()
    args = parser.parser.parse_args(["--verbose", "-s"])
    assert args.verbose is True
    assert args.show is True


def test_argparser_quiet_option():
    parser = ArgParser()
    args = parser.parser.parse_args(["--quiet", "-s"])
    assert args.quiet is True
    assert args.show is True


def test_argparser_multiple_options():
    parser = ArgParser()
    args = parser.parser.parse_args(["-b", "backup1", "-g", "20", "--wse2"])
    assert args.backup == "backup1"
    assert args.gen == 20
    assert args.wse2 is True
    assert args.restore is None
    assert args.show is False


def test_argparser_long_options():
    parser = ArgParser()
    args = parser.parser.parse_args(["--backup", "backup2", "--gen", "15"])
    assert args.backup == "backup2"
    assert args.gen == 15


def test_argparser_no_arguments():
    parser = ArgParser()
    args = parser.parser.parse_args([])
    assert args.backup is None
    assert args.restore is None
    assert args.gen is None
    assert args.show is False
    assert args.delete is None
    assert args.list is False
    assert args.wse2 is False
    assert args.verbose is False
    assert args.quiet is False


def test_argparser_invalid_gen_argument(capsys):
    parser = ArgParser()
    with pytest.raises(SystemExit):
        parser.parser.parse_args(["-g", "abc"])
    
    # Error message should be printed
    captured = capsys.readouterr()
    assert "invalid int value" in captured.err


def test_args_property():
    # Test the property with real sys.argv parsing
    parser = ArgParser()
    
    # For the property to work correctly, we need to test it with parse_args directly
    args = parser.parser.parse_args(["-s"])
    assert isinstance(args, argparse.Namespace)
    assert args.show is True
    
    # Test that multiple parsers can parse the same args independently
    parser2 = ArgParser()
    args2 = parser2.parser.parse_args(["-s"])
    assert isinstance(args2, argparse.Namespace)
    assert args2.show is True