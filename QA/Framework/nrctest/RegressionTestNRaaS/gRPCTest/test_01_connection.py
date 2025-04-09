import sys
import os

if os.path.isdir(os.path.join(os.path.dirname(__file__), '../../', './NRCSetupClass')):
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../', './NRCSetupClass'))
else:
    raise ImportError("No Such path to the NRCSetup Class")

import time

from Framework.nrctest.NRCSetupClass.TestFixture import TestFixture
from Framework.nrctest.NRCSetupClass.gRPCClient import gRPCClient, TimeoutException

# ------- NRC automation test class -----------
class NRCTestConnection(TestFixture):
    """ NRC gRPC test"""

    def test002_NRCgRPCConnectOk(self):
        """
        Test NRC gRPC connect ok - default audio (one.ulaw) with default recognize parameter & config
        Expect NRC gRPC init -> connect -> audio -> recognize successfully
        """
        client = gRPCClient()
        #
        test_expect = "<result>.+\/result>"
        #
        try:
            # test nrc connect
            test_result = client.qa_nr_recognize_test_func1()
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test005_NRCgRPCSecureConnectSetViaConfigParam(self):
        """
        [Semi-auto Test] Test NRC gRPC secure connection set via QA global config file with NRCTestSecureConnect set to true, then run test via uri-grammar recognition to verify
        Expect: NRC recognize return successful with secure connect enabled via config file
        Note: Manual set first! Update QA global config file 'testServerconfig.yaml', set param 'NRCTestSecureConnect' to true
              then run this semi-automation test case, and check test log, expect to see NRC gRPC test server secure URL nrc:50052
        """
        client = gRPCClient()   # secure connection
        #
        test_audio = 'yes.ulaw'
        test_grammar = "uri_grammar_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")  # for debug
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        test_expect2 = 'nrc:50052'  # secure connection

        test_url = str(client.test_url)
        #
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            # self.assertRecognitionResult(inputToCheck=test_url, expectResult=test_expect2)    # remove this comment after set param 'NRCTestSecureConnect' to true

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test006_NRCgRPCSecureConnectSetViaConfigPort(self):
        """
        [Semi-auto Test] Test NRC gRPC secure connection set via QA global config file with NRCSecureServicePort set to 50052, then run test via uri-grammar recognition to verify
        Expect: NRC recognize return successful with secure connect enabled via config file NRCSecureServicePort setting (check test log)
        Note: Manual set first! Update QA global config file 'testServerconfig.yaml', enable & set param 'NRCSecureServicePort' to 50052; make sure NRCTestSecureConnect set to False
              then run this semi-automation test case, and check test log, expect to see NRC gRPC test server secure URL nrc:50052

        """
        # [Manual set] Update QA global config file 'testServerconfig.yaml', set param 'NRCSecureServicePort' to 50052;
        # [Manual set] make sure NRCTestSecureConnect set to False
        client = gRPCClient()   # secure connection
        #
        test_audio = 'yes.ulaw'
        test_grammar = "uri_grammar_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")  # for debug
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        test_expect2 = 'nrc:50052'  # secure connection

        test_url = str(client.test_url)
        #
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            # self.assertRecognitionResult(inputToCheck=test_url, expectResult=test_expect2)    # remove this comment after set param 'NRCSecureServicePort' to 50052

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test007_NRCGlobalAuthToken(self):
        """
        Test NRC/NRaaS to get token from global auth in CD4
        Expect: Return auth token
        """
        client = gRPCClient()   # secure connection
        #
        test_expect = ".+"
        #
        try:
            test_result = client.get_GAtoken()
            msg = "Test result:\n" + str(test_result) + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)


"""
    def test002_gRPCConnectWrongServer(self):
        # Test NRC gRPC with wrong server
        # Expect NRC connect fail
        client = gRPCClient(gRPC_server='xxx', gRPC_port=50000)
        try:
            # validate command response
            self.assertNotEqual(client, {})

            test_audio = "one.ulaw"
            test_recInit = None
            test_result = client.clientRecognizeNegativeTest(audiofile=test_audio, recInit=test_recInit)
            test_expect = 'Error found on gRPC'
            #
            msg = "Test URL: " + client.test_url
            # msg += "\nTest result:\n" + str(test_result) + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            # self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
"""
