#!/usr/bin/env python
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Author: Alex Fore
# Copyright (c) 2024, by the California Institute of Technology. ALL RIGHTS
# RESERVED. United States Government Sponsorship acknowledged.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os
import shutil
import argparse
import subprocess
import contextlib
import tarfile
import logging

LOGGER = logging.getLogger('run_extract_test.py')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-l', '--log-level', default='info', help='Logger log level')
    parser.add_argument(
        '--old', default=False, action='store_true',
        help='Use old command line interface')
    args = parser.parse_args()

    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_level = {
        'debug': logging.DEBUG, 'info': logging.INFO,
        'warning': logging.WARNING, 'error': logging.ERROR}[args.log_level]
    logging.basicConfig(level=log_level, format=FORMAT)

    def run_subproc(exec_string, message, raise_exception=False):
        """Helper function to run subprocess and handle return values"""
        return_code = subprocess.call(exec_string, shell=True)
        if return_code != 0:
            LOGGER.error('%s failed!' % message)
            if raise_exception:
                raise Exception('%s failed!' % message)

    with contextlib.suppress(FileNotFoundError):
        shutil.rmtree('golden_test_inputs/extract')

    # Uncompress .tar.gz file with input data in it
    with tarfile.open(
            os.path.join('golden_test_inputs/extract.tar.gz')) as tar:
        tar.extractall('golden_test_inputs')

    with contextlib.suppress(FileNotFoundError):
        shutil.rmtree('test_outputs/extract')
    os.makedirs('test_outputs/extract')

    # extract azimuth angle
    exec_string = (
        'ariaExtract.py -f "golden_test_inputs/extract/products/*.nc" '
        '-l azimuthAngle -d golden_test_inputs/extract/DEM/glo_90.dem '
        '-w test_outputs/extract/')
    if not args.old:
        exec_string += ' --log-level %s' % args.log_level
    run_subproc(exec_string, 'ariaExtract azimuthAngle', raise_exception=True)

    # extract troposhere
    exec_string = (
        'ariaExtract.py -f "golden_test_inputs/extract/products/*.nc" '
        '-l troposphereTotal -tm HRRR '
        '-d golden_test_inputs/extract/DEM/glo_90.dem '
        '-w test_outputs/extract/')
    if not args.old:
        exec_string += ' --log-level %s' % args.log_level
    run_subproc(
        exec_string, 'ariaExtract troposphereTotal', raise_exception=True)

    # extract coherence
    exec_string = (
        'ariaExtract.py -f "golden_test_inputs/extract/products/*.nc" '
        '-l coherence -w test_outputs/extract/ -of ENVI')
    if not args.old:
        exec_string += ' --log-level %s' % args.log_level
    run_subproc(exec_string, 'ariaExtract coherence')

    # extract unwrapped phase
    exec_string = (
        'ariaExtract.py -f "golden_test_inputs/extract/products/*.nc" '
        '-l unwrappedPhase -w test_outputs/extract/')
    if not args.old:
        exec_string += ' --log-level %s' % args.log_level
    run_subproc(
        exec_string, 'ariaExtract unwrappedPhase', raise_exception=True)

    # extract ionosphere
    # This command fails using either branch of aria-tools...
    exec_string = (
        'ariaExtract.py -f "golden_test_inputs/extract/products/*.nc" '
        '-l ionosphere -w test_outputs/extract/')
    if not args.old:
        exec_string += ' --log-level %s' % args.log_level
    run_subproc(exec_string, 'ariaExtract ionosphere', raise_exception=True)


if __name__ == "__main__":
    main()
