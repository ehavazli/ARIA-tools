import click
from aria_tools.scripts.ariaDownload import cli_download

@click.group()
def cli():
    """ARIA-Tools: A CLI tool for downloading and processing InSAR data."""
    pass

cli.add_command(cli_download, name="download")

if __name__ == "__main__":
    cli()

