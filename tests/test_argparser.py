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


def test_argparser_help_option(monkeypatch, capsys):
    test_args = ["mb-app", "-h"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    parser = ArgParser()
    with pytest.raises(SystemExit) as exc_info:
        _ = parser.args
    assert exc_info.value.code == 0
    
    # Help should be printed
    captured = capsys.readouterr()
    assert "usage:" in captured.out


def test_argparser_version_option(monkeypatch, capsys):
    test_args = ["mb-app", "-v"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    parser = ArgParser()
    with pytest.raises(SystemExit) as exc_info:
        _ = parser.args
    assert exc_info.value.code == 0
    
    # Version should be printed
    captured = capsys.readouterr()
    assert __version__ in captured.out


def test_argparser_backup_option(monkeypatch):
    test_args = ["mb-app", "-b", "test_backup"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    parser = ArgParser()
    args = parser.args
    assert args.backup == "test_backup"
    assert args.restore is None
    assert args.gen is None
    assert args.show is False


def test_argparser_show_option(monkeypatch):
    test_args = ["mb-app", "-s"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    parser = ArgParser()
    args = parser.args
    assert args.show is True
    assert args.backup is None
    assert args.restore is None
    assert args.gen is None


def test_argparser_restore_option(monkeypatch):
    test_args = ["mb-app", "-r", "test_restore"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    parser = ArgParser()
    args = parser.args
    assert args.restore == "test_restore"
    assert args.backup is None
    assert args.gen is None
    assert args.show is False


def test_argparser_generate_option(monkeypatch):
    test_args = ["mb-app", "-g", "10"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    parser = ArgParser()
    args = parser.args
    assert args.gen == 10
    assert args.backup is None
    assert args.restore is None
    assert args.show is False


def test_argparser_delete_option(monkeypatch):
    test_args = ["mb-app", "-d", "TestChar"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    parser = ArgParser()
    args = parser.args
    assert args.delete == "TestChar"


def test_argparser_list_option(monkeypatch):
    test_args = ["mb-app", "-l"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    parser = ArgParser()
    args = parser.args
    assert args.list is True
    assert args.backup is None
    assert args.restore is None
    assert args.gen is None
    assert args.show is False


def test_argparser_wse2_option(monkeypatch):
    test_args = ["mb-app", "--wse2", "-g", "5"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    parser = ArgParser()
    args = parser.args
    assert args.wse2 is True
    assert args.gen == 5


def test_argparser_verbose_option(monkeypatch):
    test_args = ["mb-app", "--verbose", "-s"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    parser = ArgParser()
    args = parser.args
    assert args.verbose is True
    assert args.show is True


def test_argparser_quiet_option(monkeypatch):
    test_args = ["mb-app", "--quiet", "-s"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    parser = ArgParser()
    args = parser.args
    assert args.quiet is True
    assert args.show is True


def test_argparser_multiple_options(monkeypatch):
    test_args = ["mb-app", "-b", "backup1", "-g", "20", "--wse2"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    parser = ArgParser()
    args = parser.args
    assert args.backup == "backup1"
    assert args.gen == 20
    assert args.wse2 is True
    assert args.restore is None
    assert args.show is False


def test_argparser_long_options(monkeypatch):
    test_args = ["mb-app", "--backup", "backup2", "--gen", "15"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    parser = ArgParser()
    args = parser.args
    assert args.backup == "backup2"
    assert args.gen == 15


def test_argparser_no_arguments(monkeypatch):
    test_args = ["mb-app"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    parser = ArgParser()
    args = parser.args
    assert args.backup is None
    assert args.restore is None
    assert args.gen is None
    assert args.show is False
    assert args.delete is None
    assert args.list is False
    assert args.wse2 is False
    assert args.verbose is False
    assert args.quiet is False


def test_argparser_invalid_gen_argument(monkeypatch, capsys):
    test_args = ["mb-app", "-g", "abc"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    parser = ArgParser()
    with pytest.raises(SystemExit):
        _ = parser.args
    
    # Error message should be printed
    captured = capsys.readouterr()
    assert "invalid int value" in captured.err


def test_args_property(monkeypatch):
    test_args = ["mb-app", "-s"]
    monkeypatch.setattr(sys, "argv", test_args)
    
    parser1 = ArgParser()
    parser2 = ArgParser()
    
    # Test that args property returns Namespace
    args1 = parser1.args
    args2 = parser2.args
    
    assert isinstance(args1, argparse.Namespace)
    assert isinstance(args2, argparse.Namespace)
    assert args1.show is True
    assert args2.show is True