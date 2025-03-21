from setuptools import setup, find_packages

setup(
    name="aria-tools",
    version="1.3.0",
    description="A CLI tool for downloading, processing, and visualizing InSAR data.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/aria-tools/ARIA-tools",
    packages=find_packages(),
    python_requires=">=3.8",

    entry_points={
        "console_scripts": [
            "aria-tools=aria_tools.cli:cli",
        ],
    },
)
