#!python
# encoding: utf-8
"""
Common Python test utility for different QA projects like: NLPS, NRM, NRC

"""

import sys
import os
import logging
import unittest
import xmlrunner
import pkgutil
import inspect
import re
import time
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

if os.environ.get('TESTSERVICE')=='cloudtest':
    sys.path.append(os.environ.get('TESTPATH')+'/ev2/Scripts/Framework/nrctest/NRCSetupClass')
else:
    sys.path.append('/package/unarchive/Framework/nrctest/NRCSetupClass')

from TestContext import *



__all__ = []
__version__ = 1.0
__date__ = '2020-08-01'
__updated__ = '2020-08-01'

DEBUG = 1
TESTRUN = 0
PROFILE = 0
RERUN = False
RERUN_NUMBER = 0  # To store the current rerun attempt count
# failedtestcases
FAILEDTESTCASES = []


def list_files(dir):
    r = []
    subdirs = [x for x in os.listdir(dir)]
    for folder in subdirs:
        if folder.find("test_") != -1:
            r.append(folder)

    return r


def consume_flags(args):
    """Validates special flags appended to command"""
    if args.clog == True:
        # Set environment variable
        os.environ["CLOG_switch"] = "True"
        print("\nCall logging automation ENABLED: will validate test cases where KafkaModule added.\n")
    if args.clog == False:
        # Set environment variable
        os.environ["CLOG_switch"] = "False"
    if args.r == True:
        # Set environment variable
        os.environ["rerun_mode"] = "True"
        print("\nRe-run failed cases mode is enabled: will retry failed cases according to number of retry set in yaml config\n")
    if args.r == False:
        # Set environment variable
        os.environ["rerun_mode"] = "False"


def extract_failed_testcases(failed_test_error):

    # This function will get the exact name and testsuitname of the failed test cases
    test_grp = ''
    test_method = ''
    # testgroup
    s = re.search('test_[0-9]+_\S+py', failed_test_error, re.I)
    if s:
        test_grp = s.group()[:-3]
    else:
        print('Failed testcase Id not found')

    # file name
    s = re.search('test[0-9]+_\S+', failed_test_error, re.I)
    if s:
        test_method = s.group()
    else:
        print('Failed testcase Id not found')

    # Class name
    testClassName = test_grp.split('_')[-1]

    # Final test case path for re-execution
    x = test_grp + '.NRCTest' + \
        testClassName[0].upper() + testClassName[1:] + '.' + test_method

    return x


def main(argv=None):  # IGNORE:C0111
    '''Command line options.'''
    global FAILEDTESTCASES
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (
        program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = program_shortdesc + '/nNuance Communication 2020/n'

    try:
        # Setup argument parser
        parser = ArgumentParser(
            description=program_license,
            formatter_class=RawDescriptionHelpFormatter)

        parser.add_argument(
            "-x", "--xml",
            dest="make_xml", action="store_true",
            help="produce XML reports [default: %(default)s]")
        parser.add_argument(
            "-o", "--output",
            dest="output", metavar='DIR',
            default=os.path.relpath(os.path.join(
                os.path.dirname(__file__), 'log')),
            help="directory for XML reports [default: %(default)s]")
        parser.add_argument(
            "-v", "--verbose",
            dest="verbose", action="count",
            help="set verbosity level [default: %(default)s]")
        parser.add_argument(
            '-V', '--version',
            action='version', version=program_version_message)
        parser.add_argument(
            dest="testsets", metavar="testsets", nargs='*',
            help="test sets to execute [default: <all>]")
        parser.add_argument(
            "-clog", action="store_true", default=False,
            help="enables call logging automation module to validate test case where KafkaModule added [default: call logging OFF]"
        )
        parser.add_argument(
            "-r", action="store_true", default=False,
            help="enables failed test cases re-run mode where the framework will attempt to rerun failed cases. The number of re-run attempts is set in the yaml config"
        )

        # Process arguments
        args = parser.parse_args()
        consume_flags(args)

        # Define the suite of tests. By default, include all of the tests.
        loader = unittest.TestLoader()
        tests = unittest.TestSuite()

        if len(args.testsets) == 0:
            tests = unittest.TestLoader().discover(
                os.path.dirname(__file__), pattern="test_*.py")

        # check if there are any failed test, if yes add them to the tests object
        elif RERUN:

            # logic to add tests from the reruntests list
            folderPath = os.path.join(os.path.dirname(
                __file__), './', args.testsets[0])
            if os.path.isdir(folderPath) == True:
                sys.path.append(folderPath)
            l = []

            for failedtc in FAILEDTESTCASES:
                l.append(failedtc)
                __import__(failedtc.split('.')[0])
            tests = loader.loadTestsFromNames(l)
            # Reset failed list
            FAILEDTESTCASES = []

        # Include the named sub-sets of tests.
        elif len(args.testsets) == 1:
            folderPath = os.path.join(os.path.dirname(
                __file__), './', args.testsets[0])
            if os.path.isdir(folderPath) == True:
                # Remove undesired test groups based on the flags
                tests = None
                for file in os.listdir(folderPath):
                    #
                    # Call logging environment variable not set => skip test group 07
                    if file == "test_07_callLogging.py" and args.clog == False:
                        continue
                    #
                    #
                    if tests == None:
                        tests = loader.discover(os.path.join(os.path.dirname(
                            __file__), './', args.testsets[0]), pattern=file)
                    else:
                        tests.addTests(loader.discover(os.path.join(
                            os.path.dirname(__file__), './', args.testsets[0]), pattern=file))
            #
            else:
                raise ImportError("No such folder")

        elif len(args.testsets) > 1:
            folderPath = os.path.join(os.path.dirname(
                __file__), './', args.testsets[0])
            if os.path.isdir(folderPath) == True:
                sys.path.append(folderPath)
            # Import the specified test modules starting from the 2 argument.
            for name in args.testsets[1:]:
                parts = name.split('.')
                try:
                    test_group = parts[0]
                    #
                    # Call logging environment variable not set => skip test group 07
                    if test_group == "test_07_callLogging" and not args.clog:
                        return
                    #
                    #
                    __import__(test_group)

                except ImportError:
                    pass

            # Load the matching tests.
            tests = loader.loadTestsFromNames(args.testsets[1:])

        # Initialize test run logging. In general, the root logger logs
        # nothing. Logging output is only produced, when the test
        # fixture configures a test case log handler.
        logging.basicConfig(filename=os.devnull, level=logging.DEBUG)
        # logging.basicConfig(filename=os.devnull, level=logging.INFO)

        # Select the output format.
        if args.make_xml:
            suffix = ""
            if (RERUN):
                suffix = '{}__RERUN{}'.format(
                    time.strftime("%Y%m%d%H%M%S"), RERUN_NUMBER)
            else:
                suffix = '{}__MAIN'.format(time.strftime("%Y%m%d%H%M%S"))
            runner = xmlrunner.XMLTestRunner(
                output=args.output, verbosity=args.verbose, outsuffix=suffix)
            # runner = xmlrunner.XMLTestRunner(output=args.output, verbosity=2)
        else:
            runner = unittest.TextTestRunner(verbosity=args.verbose)

        # return not runner.run(tests).wasSuccessful()
        testresult = runner.run(tests)

        # collect failed test cases
        rerun_tests = []

        if len(testresult.failures) > 0:
            for failed_case in testresult.failures:
                rerun_tests.append(
                    extract_failed_testcases(failed_case[-1]))

        if len(testresult.errors) > 0:
            for error_case in testresult.errors:
                rerun_tests.append(extract_failed_testcases(
                    error_case[-1]))

        rerun_tests
        return rerun_tests
        # return not testresult.wasSuccessful()
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0

    except Exception as e:
        if DEBUG or TESTRUN:
            raise (e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2


if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-v")
    if TESTRUN:
        import doctest

        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats

        profile_filename = 'nrctest_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)

    FAILEDTESTCASES = main()
    context = TestContext()

    if os.environ["rerun_mode"] == "True":
        for retry_number in range(1, int(context.config['NRCTestRetryFailedTestCases'])+1):
            if FAILEDTESTCASES:
                print('\t\t\n <-----> Failure Retry <----->'*5 +
                      '\t\t\n\n\n Sleeping for 20Sec \n\n\n\n\n This is Failed TestCases RETRY # ' + str(retry_number))
                RERUN = True
                RERUN_NUMBER += 1
                time.sleep(20)
                FAILEDTESTCASES = main()
    sys.exit(0)
    # sys.exit(main())
# sys.exit(0)
