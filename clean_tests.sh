#!/bin/bash

# clean_tests.sh — Cleanup script for ARIA-tools test artifacts

echo "Cleaning test-generated files..."

# Remove Python cache files
find . -type d -name "__pycache__" -exec rm -r {} +
rm -rf .pytest_cache
rm -rf .mypy_cache

# Remove common output directories
rm -rf products/
rm -rf downloads/
rm -rf output/

# Remove log files or temp configs (if any)
rm -f *.log
rm -f tmp_*.yml

echo "Done cleaning."

