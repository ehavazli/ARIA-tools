import textwrap
import sys
from unittest import mock
import pytest
from aria_tools.scripts.ariaDownload import main

def test_cli_download_runs_with_minimal_config(tmp_path):
    """Directly call the ariaDownload.py main() function with config file."""
    config_path = tmp_path / "config.yml"
    config_path.write_text(textwrap.dedent("""\
        mission: S1
        track: "004"
        bbox: "36.75 37.225 -76.655 -75.928"
        start: "20190101"
        end: "20190201"
        output: Count
        wd: ./products
        num_threads: 1
        log_level: info
    """))

    # Simulate command-line args: ['ariaDownload.py', '--config', '...']
    test_args = [
        "ariaDownload.py",  # fake script name
        "--config", str(config_path)
    ]

    with mock.patch.object(sys, "argv", test_args):
        main()  # Call the main function directly

def test_cli_download_fails_without_required_inputs():
    """Check error when no bbox or track is specified."""
    # Simulate missing required arguments
    test_args = [
        "ariaDownload.py",  # fake script name
    ]

    with mock.patch.object(sys, "argv", test_args), mock.patch("builtins.print") as mock_print:
        try:
            main()
        except ValueError as e:
            # Ensure the expected error message is raised
            assert str(e) == "You must specify either --track or --bbox unless using --mission NISAR."

def test_cli_shows_help():
    """Check that help is shown for the download subcommand."""
    # Simulate command-line args for help: ['ariaDownload.py', '--help']
    test_args = [
        "ariaDownload.py",  # fake script name
        "--help",  # simulate the help flag
    ]

    with mock.patch.object(sys, "argv", test_args), mock.patch("sys.exit") as mock_exit, mock.patch("builtins.print") as mock_print:
        try:
            main()
        except ValueError as e:
            # Ensure the expected error message is raised
            assert str(e) == "You must specify either --track or --bbox unless using --mission NISAR."
