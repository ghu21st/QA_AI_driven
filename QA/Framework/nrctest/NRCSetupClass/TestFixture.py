"""
Common Test Case Fixture

"""
from __future__ import print_function
from hashlib import sha256

import logging
import os
import re
import sys
import time
import traceback
import unittest
from datetime import datetime

from TestContext import TestContext


class TestFixture(unittest.TestCase):

    def setUp(self):
        """Allocate test case resources."""

        # Initialize the test context.
        TestContext.flush()
        context = TestContext()
        self.root_dir = context.root_dir

        # Create a test log folder based on the test case
        # name and a timestamp.
        self.log_dir = os.path.join(
            context.log_base,
            datetime.fromtimestamp(time.time()).\
            strftime('%Y%m%dT%H%M%S-' + self.id()))
        try:
            os.makedirs(self.log_dir)
        except os.error:
            pass
        context.log_dir = self.log_dir

        # Initialize test case logging. This is done by adding a
        # test case-specific handler to the root logger.
        log_file = os.path.join(
            self.log_dir, self.id().split('.').pop() + '.log')
        self.log_handler = logging.FileHandler(filename=log_file)
        self.log_handler.setFormatter(logging.Formatter(
            fmt='%(asctime)s|%(levelname)s|%(message)s'))
        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_handler)

        # Mark the start of the test case log.
        self.info('Test case started.')

    def tearDown(self):
        """Perform test case cleanup."""
        # Log the results of the test case.
        exctype, value, tb = sys.exc_info()
        if not exctype:
            self.info("Test result: Success")
        elif exctype is self.failureException:
            self.warning(
                self._get_failure_message(exctype, value, tb))
            self.info("Test result: FAILURE")
        else:
            self.error(
                self._get_error_message(exctype, value, tb))
            self.info("Test result: ERROR")

        # Display test case name at the end
        print("\nRan test case:", self.id(), "\n-------\n")

        # Remove the test case-specific log handler.
        root_logger = logging.getLogger()
        root_logger.removeHandler(self.log_handler)
        self.log_handler.close()

    def exception(self, *args, **kwargs):
        '''Log an exception.'''
        logger = logging.getLogger(__name__)
        logger.exception(*args, **kwargs)

    def error(self, *args, **kwargs):
        '''Log an error message.'''
        logger = logging.getLogger(__name__)
        logger.error(*args, **kwargs)

    def warning(self, *args, **kwargs):
        '''Log a warning message.'''
        logger = logging.getLogger(__name__)
        logger.warning(*args, **kwargs)

    def info(self, *args, **kwargs):
        '''Log an informational message.'''
        logger = logging.getLogger(__name__)
        logger.info(*args, **kwargs)

    def debug(self, *args, **kwargs):
        '''Log a debug message.'''
        logger = logging.getLogger(__name__)
        logger.debug(*args, **kwargs)

    # ---------------------------------------------------
    # Define a function for NRC test result check
    def assertRecognitionResult(self, inputToCheck=None, expectResult=None):
        if None == inputToCheck:
            inputToCheck = ""
        if None == expectResult:
            expectResult = '<result>.+\/result>'
        #
        logger = logging.getLogger(__name__)
        msg = '\nActual recognition result: ' + inputToCheck
        msg += '\nTest expected result: ' + expectResult
        logger.info(msg)
        # print(msg)    # for debug
        # Validation
        pattern = re.compile(expectResult)
        ret = pattern.search(inputToCheck)
        #
        if ret:
            # check passed, return True
            msg = 'Assert recognition validation... Passed!\n'
        else:
            # check failed, return False
            msg = 'Assert recognition validation... Failed!\n'
        #
        logger.info(msg)
        # print(msg)  # for debug
        self.assertTrue(ret)
        return ret

    # Assertion check undesired expression is not part of the result.
    def assertNotRecognitionResult(self, inputToCheck=None, undesiredResult=None):
        if None == inputToCheck or inputToCheck == "" or None == undesiredResult or undesiredResult == "":
            print("Invalid input!")
            return True
        #
        pattern = re.compile(undesiredResult)
        ret = pattern.search(inputToCheck)
        #
        if ret:
            # check passed, return False
            msg = "Expression is present in the result... Failed!"
        else:
            # check faield, return True
            msg = "Expression is not present in the result... Passed!"
        #
        print(msg)
        self.assertFalse(ret)
        return not ret
        
    # -------------------------------------------------------
    
    # Extract xml content from first occruence in recognition result.
    def getFirstXmlOccurrence(self, xmlTarget=None, result=None):
        if xmlTarget == None  or xmlTarget == "":
            raise Exception("Invalid xmlTarget argument (None or empty string)")
        
        # Extract substring between 2 markers: <xmlTarget> and </xmlTarget> 
        match_obj = re.search('<' + xmlTarget + '.+>(.+?)<\/' + xmlTarget + '>', result)

        # If no result found, raise exception.
        if not match_obj:
            raise Exception("No " + xmlTarget + " tags found in: " + result)
        
        # return content as string
        return str(match_obj.group(1))
        
    # -------------------------------------------------------

    # Generate SHA256 from input string.
    def generateSHA256(self, input):
        return sha256(str(input).encode('utf-8')).hexdigest()
        
    # -------------------------------------------------------

    @staticmethod
    def open_media_file(media_path):
        '''Get an open handle to a media resource.

        This is used in application server push request.

        Args:
            media_path (str): Relative path of the resource.

        Returns:
            Open handle ('rb' mode) to the media resource.
        '''
        media_file = os.path.join(
            TestContext().media_dir, media_path)
        return open(media_file, 'rb')

    def assertMatch(self, actual, regex, msg=None, flags=0):
        '''Assert against a regular expression match.

        Compares against the start of the actual value.

        Args:
            actual (str): Actual value to compare
            regex (regex): Regular expression to compare against
            msg (str): Optional failure message
            flags (int): Optional regular expression flags

        Throws:
            AssertException: Values do not match.
        '''
        if msg == None:
            msg = 'Regex mismatch ("{}" != /{}/)'.format(actual, regex)
        self.assertTrue(re.match(regex, actual, flags), msg)

    def assertSearch(self, actual, regex, msg=None, flags=0):
        '''Assert against a regular expression search.

        Looks for the pattern anywhere in the actual value.

        Args:
            actual (str): Actual value to compare
            regex (regex): Regular expression to compare against
            msg (str): Optional failure message
            flags (int): Optional regular expression flags

        Throws:
            AssertException: Values do not match.
        '''
        if msg == None:
            msg = 'Regex not found ("{}" != /{}/)'.format(actual, regex)
        self.assertTrue(re.search(regex, actual, flags), msg)

    def assertInRange(self, actual, minimum, maximum, msg=None):
        """Assert against a value range.

        The expected value range is inclusive. The values can be any
        type that support the "<" and ">" operands.

        Args:
            actual (any): Actual value to compare.
            minimum (any): Expected minimum value.
            maximum (any): Expected maximum value.
            msg (str): Optional failure message.

        Throws:
            AssertException: Value out of range.
        """
        if not msg:
            self.assertFalse(
                actual < minimum,
                "Value out of range ('{}' < '{}')".format(
                    actual, minimum))
            self.assertFalse(
                actual > maximum,
                "Value out of range ('{}' > '{}')".format(
                    actual, maximum))
        else:
            self.assertFalse(actual < minimum, msg)
            self.assertFalse(actual > maximum, msg)

    def assertStatusCode(self, actual, expect, msg=None):
        '''Assert against a response status code.

        Args:
            actual (int): Actual HTTP response status code
            expect (int): Expected response status code
            msg (str): Optional failure message

        Throws:
            AssertException: Status code does not match.
        '''
        if msg == None:
            msg = 'Status code mismatch ({:d} != {:d})'\
                .format(actual, expect)
        self.assertEqual(actual, expect, msg)

    def assertContent(
            self, actual, expect,
            msg="Content mismatch ('{actual}' != '{expect}')"):
        '''Assert against the content of a response.

        Args:
            actual (str): Actual content of the response.
            expect (str): Expected content of the response.
            msg (str): Error message format. Can use "actual" and
                "expect" placeholders.

        Throws:
            AssertException: Status code does not match.
        '''
        self.assertEqual(
            actual, expect, msg.format(actual=actual, expect=expect))

    def assertChannels(self, actual, expect):
        '''Calls AssertChannelsLinks to check link number
        for non streaming, thus does not check for partial_lattice'''
        self.assertChannelsLinks(actual,expect,False)

    def assertSpeaker(self, actual, expect, transcript=False):
        '''Expected format:

                "links": {
                    "2": {
                        "speaker": 3
                    }
                }}

            Args:
            actual (dict): Actual channel data.
            expect (dict): Expected channel parameters.
            transcript (Bool): Tells if input is transcript mode or lattice mode

            Checks to see if all text in expected is found and then compares their speaker number
            NOTE: For transcript, text field must contain the entire text'''
        numExpect = 0
        numActual = 0
        enterLoop = 0
        if(transcript):
            #Loops through all items in the list
            for items in expect['transcript']:
                #For each item inside the expected list, loop through the entire actual response
                for tactual in actual['transcript']:
                    #If the text matches then compare the speaker number
                    if(actual['transcript'][numActual]['text'] == expect['transcript'][numExpect]['text']):
                        self.assertEqual(expect['transcript'][numExpect]['speaker'],
                        int(actual['transcript'][numActual]['speaker']), "Speaker Mismatch in speaker number '{}', actual speaker '{}'".format(
                            expect['transcript'][numExpect]['speaker'],actual['transcript'][numActual]['speaker']))
                        enterLoop += 1
                    numActual += 1
                numExpect += 1
                numActual = 0
            #Checks that all text in the expected list has been found
            self.assertEqual(enterLoop,len(expect['transcript']),"One or more text not found!")
        else:
            #Loops through all links
            for lname, lexpect in expect['links'].iteritems():
                #Compares the speaker number in the link specified in the input is equal
                #to that of the actual json output
                self.assertEqual(lexpect['speaker'],
                actual['links'][lname]['speaker'],
                "Speaker Mismatch")


    def assertNumSpeakers(self, actual, numSpeakers, transcript=False):
        '''Checks for the total number of speakers

        Args:
            actual (dict): Actual link data.
            numSpeaker (int): Expected number of speakers.
            transcript (bool): Defines if result format is in transcript or lattice'''

        maxSpeakers=0
        itemNum = 0
        if (transcript):
            for items in actual:
                if(maxSpeakers < actual[itemNum]['speaker']):
                    maxSpeakers = actual[itemNum]['speaker']
                itemNum += 1
        else:
            for lname, lactual in actual.iteritems():
                if(maxSpeakers < actual[lname]['speaker']):
                    maxSpeakers = actual[lname]['speaker']

        self.assertEqual(int(maxSpeakers), numSpeakers, "Number of Speakers Mismatch: '{}' found, '{}' expected".format(maxSpeakers, numSpeakers))

    def assertChannelsStream(self,actual,expect):
        '''Calls AssertChannelsLinks to check link number
        for streaming, thus also checks for partial_lattice'''
        self.assertChannelsLinks(actual,expect,True)

    def assertChannelsLinks(self,actual,expect,stream):
        '''Assert the general structure of result channel data.

        Example expected channel data:

            {
                "firstChannelLabel": {
                    "errors": 0,
                    "lattice": {"1": {"links": 2}}}}

            This will match a single "firstChannelLabel" channel, no
            errors and a "1" lattice containing two links.

        Args:
            actual (dict): Actual channel data.
            expect (dict): Expected channel parameters.

        Throws:
            AssertException: Channel data mismatch.
        '''

        # Check the output channels.
        channels_actual = list(actual.keys())
        channels_expect = list(expect.keys())
        self.assertEqual(
            channels_actual, channels_expect,
            "Channel mismatch ({} != {})"\
            .format(channels_actual, channels_expect))

        for cname, cactual in actual.iteritems():
            cexpect = expect[cname]

            # Check the transcription errors.
            self.assertIn(
                'errors', cactual,
                "Channel '{}' missing error set".format(cname))
            errors_actual = len(cactual['errors'])
            self.assertEqual(
                errors_actual, cexpect['errors'],
                "Channel '{}' error count mismatch ({} != {})"\
                .format(cname, errors_actual, cexpect['errors']))

            # Check the expected lattice set.
            if 'lattice' in cexpect:
                self.assertIn(
                    'lattice', cactual,
                    "Channel '{}' missing lattice set".format(cname))
                lattices_actual = list(cactual['lattice'].keys())
                lattices_expect = list(cexpect['lattice'].keys())
                self.assertEqual(
                    lattices_actual, lattices_expect,
                    "Channel '{}' lattice mismatch ({} != {})"\
                    .format(cname, lattices_actual, lattices_expect))

                # Check the link set.
                for tname, tactual in cactual['lattice'].iteritems():
                    texpect = cexpect['lattice'][tname]

                    self.assertIn(
                        'links', tactual,
                        "Lattice '{}.{}' missing links"\
                        .format(cname, tname))

                    links_actual = len(tactual['links'].keys())
                    self.assertEqual(
                        links_actual, texpect['links'],
                        "Lattice '{}.lattice.{}' link count mismatch ({} != {})"\
                        .format(cname, tname,
                                links_actual, texpect['links']))

            # Lattice set not expected in this channel.
            else:
                self.assertNotIn(
                    'lattice', cactual,
                    "Channel '{}' contains lattice set".format(cname))
            if(stream):
                # Check the expected lattice set.
                if 'partial_lattice' in cexpect:
                    self.assertIn(
                        'partial_lattice', cactual,
                        "Channel '{}' missing partial_lattice set".format(cname))
                    lattices_actual = list(cactual['partial_lattice'].keys())
                    lattices_expect = list(cexpect['partial_lattice'].keys())
                    self.assertEqual(
                        lattices_actual, lattices_expect,
                        "Channel '{}' partial_lattice mismatch ({} != {})"\
                        .format(cname, lattices_actual, lattices_expect))

                    # Check the link set.
                    for tname, tactual in cactual['partial_lattice'].iteritems():
                        texpect = cexpect['partial_lattice'][tname]

                        self.assertIn(
                            'links', tactual,
                            "Lattice '{}.{}' missing links"\
                            .format(cname, tname))

                        links_actual = len(tactual['links'].keys())
                        self.assertEqual(
                            links_actual, texpect['links'],
                            "Lattice '{}.partial_lattice.{}' link count mismatch ({} != {})"\
                            .format(cname, tname,
                                    links_actual, texpect['links']))

                # Lattice set not expected in this channel.
                else:
                    self.assertNotIn(
                        'partial_lattice', cactual,
                        "Channel '{}' contains partial_lattice set".format(cname))

    def assertChannelError(self, results,
                           channel="firstChannelLabel", index=0,
                           message=None, syscall=None,
                           errno=None, code=None):
        """Verify an expected channel error.

        At least one of the expected "message", "syscall", "errno" or
        "code" arguments is required.

        Args:
            results (dict): Required job results
            channel (str): Name of the channel. Defaults to
                "firstChannelLabel".
            index (int): Index of the error entry. Defaults to zero.
            message (regex): Expected error message. Defaults to none.
            syscall (str): Expected "channel.syscall" value. Defaults
                to none.
            errno (str): Expected "channel.errno" name. Defaults to
                none.
            code (str): Expected "channel.code" name. Defaults to
                none.

        Throws:
            ValueError: Expected error not specified.
            AssertException: Expected error not found.
        """
        if not (message or syscall or errno or code):
            raise ValueError("Expected error not specified")

        # Prepend assertion exceptions with a channel error
        # identifier.
        preface = "Channel '{}', error {}: ".format(channel, index)
        errors = results['channels'][channel]['errors']
        try:
            self.assertTrue(
                len(errors) > index, "Error not found")
            error = errors[index]

            # Check for an expected message.
            self.assertIn(
                'message', error, "Missing message")
            if message:
                self.assertMatch(
                    error['message'], message,
                    "Message mismatch ('{}' !~ '{}')"\
                    .format(error['message'], message))

            # Check the channel error info.
            self.assertIn(
                'channel', error, "Missing channel")
            channel = error['channel']

            if syscall:
                self.assertEqual(
                    channel['syscall'], syscall,
                    "SysCall mismatch ('{}' != '{}')"\
                    .format(channel['syscall'], syscall))
            if errno:
                self.assertEqual(
                    channel['errno'], errno,
                    "ErrNo mismatch ('{}' != '{}')"\
                    .format(channel['errno'], errno))
            if code:
                self.assertEqual(
                    channel['code'], code,
                    "Code mismatch ('{}' != '{}')"\
                    .format(channel['code'], code))

        # Add identification and rethrow the exception.
        except AssertionError as e:
            e.args = e.args[:-1] + (preface + e.args[-1],)
            raise

    # Get the log message for an error exception.
    def _get_error_message(self, exctype, value, tb):
        return '\n'.join(
            traceback.format_exception(exctype, value, tb))

    # Get the log message for a failure exception.
    def _get_failure_message(self, exctype, value, tb):

        # Skip test runner traceback levels
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next

        # Skip assert*() traceback levels
        length = self._count_relevant_tb_levels(tb)

        # Log it as a single entry.
        return '\n'.join(
            traceback.format_exception(exctype, value, tb, length))

    # Determine if a failure traceback level is relevant.
    def _is_relevant_tb_level(self, tb):
        return '__unittest' in tb.tb_frame.f_globals

    # Count up the relevant failure traceback levels.
    def _count_relevant_tb_levels(self, tb):
        length = 0
        while tb and not self._is_relevant_tb_level(tb):
            length += 1
            tb = tb.tb_next
            return length


if __name__ == "__main__":
    unittest.main()
