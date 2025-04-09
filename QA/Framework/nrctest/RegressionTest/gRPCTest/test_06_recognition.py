import sys
import os
import time

from importlib_metadata import NullFinder

# from Framework.nrctest.NRCSetupClass.TestFixture import TestFixture
# from Framework.nrctest.NRCSetupClass.gRPCClient import gRPCClient, TimeoutException

if os.path.isdir(os.path.join(os.path.dirname(__file__), '../../', './NRCSetupClass')):
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../', './NRCSetupClass'))
else:
    raise ImportError("No Such path to the NRCSetup Class")

from TestFixture import TestFixture
from gRPCClient import gRPCClient, TimeoutException
from KafkaModule import KafkaModule

# ------- NRC automation test class -----------
class NRCTestRecognition(TestFixture):
    """ NRC recognition test"""

    def test001_NRCRecognitionGeneric1(self):
        """
        Test NRC recognition generic 1 - recognition API with default audio, parameter & config
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = "0123456789.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+instance.+0123456789.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()
            kafka.cleanup()

    def test002_RecognitionNoMatch(self):
        """
        Test NRC recognition inline grammar (yes) without match audio input (one.ulaw)
        Expect 
        1) [Test Case] NRC recognize fail, return: SWIrec_STATUS_NO_MATCH
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check SWIrslt absent from call logs (due to NO_MATCH)
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = 'one.ulaw'
        test_grammar_data = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>hello world</item>\n<item>yes</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, result_status="NO_MATCH")
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        # test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="lowconf")
        # test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RSLT", value="{SWI_literal:one}")
        test_record_1.add_undesired_to_checklist("SWIrslt")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(3)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()
            kafka.cleanup()

    def test003_RecognitionBuiltinThenInlineGrammar(self):
        """
        Test NRC multiple recognition - builtin grammar with audio 945015260.ulaw first then inline grammar with audio one.ulaw
        Expect 
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) For both recognition requests check:
                - SWIgrld: grammar loaded
                - SWIrslt: expected recognition result, and grammar used for recognition result
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio1 = "945015260.ulaw"
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/digits.+instance>945015260</instance></interpretation>.+\</result>"

        test_recogParams1 = client.recognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)
        #
        test_audio2 = 'one.ulaw'
        test_grammar_data2 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>one</item>\n<item>yes</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type2 = 'inline_grammar'
        test_media_type2 = 'srgsxml'
        test_expect2 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>one</SWI_literal>.+<SWI_meaning.+one.+SWI_meaning></instance></interpretation></result>"

        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2, mediaType=test_media_type2)
        test_recInit2 = client.recognition_init(test_recogParams2, test_recogRes2)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect1)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")

        test_record_2 = kafka.create_messages_record(recogInit=test_recInit2, expected_result=test_expect2)
        test_record_2.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_2.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=en-US")
        test_record_2.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect2)
        test_record_2.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"FluentD redacted possible CCN\"")

        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            #
            kafka.validate_callLogs([test_record_1, test_record_2])

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()
            kafka.cleanup()

    def test004_RecognitionBuiltinThenUriGrammar(self):
        """
        Test NRC multiple recognition - builtin grammar with audio 945015260.ulaw first then Uri grammar with auidio yes.ulaw
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio1 = "945015260.ulaw"
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"

        test_recogParams1 = client.recognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)
        #
        test_audio2 = 'yes.ulaw'
        test_grammar_data2 = "uri_grammar_yes.grxml"
        test_grammar_type2 = "uri_grammar"
        test_media_type2 = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar_data2
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect2 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri, mediaType=test_media_type2)
        test_recInit2 = client.recognition_init(test_recogParams2, test_recogRes2)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test005_RecognitionInlineThenUriGrammar(self):
        """
        Test NRC multiple recognition - Inline grammar with audio one.ulaw first then uri grammar with audio yes.ulaw
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio1 = 'one.ulaw'
        test_grammar_data1 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>one</item>\n<item>yes</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type1 = 'inline_grammar'
        test_media_type1 = 'srgsxml'
        test_expect1 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>one</SWI_literal>.+<SWI_meaning.+one.+SWI_meaning></instance></interpretation></result>"

        test_recogParams1 = client.recognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1, mediaType=test_media_type1)
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)
        #
        test_audio2 = 'yes.ulaw'
        test_grammar_data2 = "uri_grammar_yes.grxml"
        test_grammar_type2 = "uri_grammar"
        test_media_type2 = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar_data2
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect2 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri, mediaType=test_media_type2)
        test_recInit2 = client.recognition_init(test_recogParams2, test_recogRes2)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test006_RecognitionUriGrammarThenInlineGrammar(self):
        """
        Test NRC multiple recognition - uri grammar with audio yes.ulaw then Inline grammar with audio one.ulaw
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio1 = 'yes.ulaw'
        test_grammar_data1 = "uri_grammar_yes.grxml"
        test_grammar_type1 = "uri_grammar"
        test_media_type1 = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar_data1
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect1 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams1 = client.recognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)
        #
        test_audio2 = 'one.ulaw'
        test_grammar_data2 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>one</item>\n<item>yes</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type2 = 'inline_grammar'
        test_media_type2 = 'srgsxml'
        test_expect2 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>one</SWI_literal>.+<SWI_meaning.+one.+SWI_meaning></instance></interpretation></result>"

        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2, mediaType=test_media_type2)
        test_recInit2 = client.recognition_init(test_recogParams2, test_recogRes2)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test007_RecognitionBuiltinThenUriGrammarThenInlineGrammar(self):
        """
        Test NRC multiple recognition - builtin grammar with audio 945015260.ulaw then Uri grammar with auidio yes.ulaw then Inline grammar with one.ulaw
        Expect 
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) For every recognition requests check:
                - SWIgrld: grammar loaded
                - SWIrslt: expected recognition result, and grammar used for recognition result
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio1 = "945015260.ulaw"
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"
        test_recogParams1 = client.recognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)
        #
        test_audio2 = 'yes.ulaw'
        test_grammar_data2 = "uri_grammar_yes.grxml"
        test_grammar_type2 = "uri_grammar"
        test_media_type2 = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar_data2
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect2 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri, mediaType=test_media_type2)
        test_recInit2 = client.recognition_init(test_recogParams2, test_recogRes2)
        #
        test_audio3 = 'one.ulaw'
        test_grammar_data3 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>one</item>\n<item>yes</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type3 = 'inline_grammar'
        test_media_type3 = 'srgsxml'
        test_expect3 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>one</SWI_literal>.+<SWI_meaning.+one.+SWI_meaning></instance></interpretation></result>"
        test_recogParams3 = client.recognition_parameters()
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_data3, mediaType=test_media_type3)
        test_recInit3 = client.recognition_init(test_recogParams3, test_recogRes3)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect1)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        test_record_2 = kafka.create_messages_record(recogInit=test_recInit2, expected_result=test_expect2)
        test_record_2.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_2.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_2.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect2)
        test_record_2.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\""+test_grammar_uri)

        test_record_3 = kafka.create_messages_record(recogInit=test_recInit3, expected_result=test_expect3)
        test_record_3.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_3.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=en-US")
        test_record_3.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect3)
        test_record_3.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"FluentD redacted possible CCN\"")

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio3, recInit=test_recInit3)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)
            #
            kafka.validate_callLogs([test_record_1, test_record_2, test_record_3])
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test008_RecognitionInlineGrammarThenBuiltinThenUriGrammar(self):
        """
        Test NRC multiple recognition - Inline grammar with one.ulaw Then builtin grammar with audio 945015260.ulaw then Uri grammar with auidio yes.ulaw
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio1 = 'one.ulaw'
        test_grammar_data1 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>one</item>\n<item>yes</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type1 = 'inline_grammar'
        test_media_type1 = 'srgsxml'
        test_expect1 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>one</SWI_literal>.+<SWI_meaning.+one.+SWI_meaning></instance></interpretation></result>"

        test_recogParams1 = client.recognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1, mediaType=test_media_type1)
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)
        #
        test_audio2 = "945015260.ulaw"
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        test_expect2 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"

        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recInit2 = client.recognition_init(test_recogParams2, test_recogRes2)
        #
        test_audio3 = 'yes.ulaw'
        test_grammar_data3 = "uri_grammar_yes.grxml"
        test_grammar_type3 = "uri_grammar"
        test_media_type3 = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar_data3
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect3 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams3 = client.recognition_parameters()
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_uri, mediaType=test_media_type3)
        test_recInit3 = client.recognition_init(test_recogParams3, test_recogRes3)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio3, recInit=test_recInit3)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test009_RecognitionUriGrammarThenInlineGrammarThenBuiltin(self):
        """
        Test NRC multiple recognition - Uri grammar with auidio yes.ulaw then Inline grammar with one.ulaw then builtin grammar with audio 945015260.ulaw
        Expect 
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) For every recognition requests check:
                - SWIgrld: grammar loaded
                - SWIrslt: expected recognition result, and grammar used for recognition result
	    """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio1 = 'yes.ulaw'
        test_grammar_data1 = "uri_grammar_yes.grxml"
        test_grammar_type1 = "uri_grammar"
        test_media_type1 = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar_data1
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect1 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        test_recogParams1 = client.recognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)
        #
        test_audio2 = 'one.ulaw'
        test_grammar_data2 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>one</item>\n<item>yes</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type2 = 'inline_grammar'
        test_media_type2 = 'srgsxml'
        test_expect2 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>one</SWI_literal>.+<SWI_meaning.+one.+SWI_meaning></instance></interpretation></result>"
        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2, mediaType=test_media_type2)
        test_recInit2 = client.recognition_init(test_recogParams2, test_recogRes2)
        #
        test_audio3 = "945015260.ulaw"
        test_grammar_type3 = 'builtin'
        test_grammar_data3 = 'digits'
        test_expect3 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"
        test_recogParams3 = client.recognition_parameters()
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_data3)
        test_recInit3 = client.recognition_init(test_recogParams3, test_recogRes3)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect1)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\""+test_grammar_uri)

        test_record_2 = kafka.create_messages_record(recogInit=test_recInit2, expected_result=test_expect2)
        test_record_2.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_2.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=en-US")
        test_record_2.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect2)
        test_record_2.add_token_to_checklist(evnt="SWIrcnd", token="RAWT", value="FluentD redacted possible CCN")

        test_record_3 = kafka.create_messages_record(recogInit=test_recInit3, expected_result=test_expect3)
        test_record_3.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_3.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_3.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect3)
        test_record_3.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio3, recInit=test_recInit3)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)
            #

            kafka.validate_callLogs([test_record_1, test_record_2, test_record_3])

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()
            kafka.cleanup()

    def test010_RecognitionInvalid_UriGrammarThenInlineGrammar(self):
        """
        Test NRC multiple recognition - Invalid uri grammar with audio yes.ulaw then valid Inline grammar with audio one.ulaw
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio1 = 'yes.ulaw'
        test_grammar_data1 = "xxxx.grxml"
        test_grammar_type1 = "uri_grammar"
        test_media_type1 = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar_data1
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        # test_expect1 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        test_expect11 = "code: 400"
        test_expect12 = 'message: \"Bad Request\"'
        test_expect13 = "details: \"Failed to load RecognitionResource"

        test_recogParams1 = client.recognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)
        #
        test_audio2 = 'one.ulaw'
        test_grammar_data2 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>one</item>\n<item>yes</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type2 = 'inline_grammar'
        test_media_type2 = 'srgsxml'
        test_expect2 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>one</SWI_literal>.+<SWI_meaning.+one.+SWI_meaning></instance></interpretation></result>"

        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2, mediaType=test_media_type2)
        test_recInit2 = client.recognition_init(test_recogParams2, test_recogRes2)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            self.debug(msg)
            print(msg)    # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect13)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)

    def test011_RecognitionInvalid_BuiltinThenValidInlineGrammar(self):
        """
        Test NRC multiple recognition - Invalid builtin grammar recognize then Valid inline grammar recognize
        Expect NRC the first recognize failed with expected return code 400 & error message and then the 2nd recognize success
        """
        client = gRPCClient()
        #
        test_audio1 = "945015260.ulaw"
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'xxxx'
        test_expect11 = "code: 400"
        test_expect12 = 'message: \"Bad Request\"'
        test_expect13 = "details: \"Failed to load RecognitionResource"

        test_recogParams1 = client.recognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)
        #
        test_audio2 = 'one.ulaw'
        test_grammar_data2 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>one</item>\n<item>yes</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type2 = 'inline_grammar'
        test_media_type2 = 'srgsxml'
        test_expect2 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>one</SWI_literal>.+<SWI_meaning.+one.+SWI_meaning></instance></interpretation></result>"

        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2, mediaType=test_media_type2)
        test_recInit2 = client.recognition_init(test_recogParams2, test_recogRes2)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1,
                                                            recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2,
                                                            recInit=test_recInit2)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect13)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)

    def test012_RecognitionInvalid_BuiltinThenValidUriGrammarThenValidInline(self):
        """
        Test NRC multiple recognition - Invalid builtin grammar recognize then valid Uri grammar recognize then Valid inline grammar recognize
        Expect 
        1) [Test Case] NRC the first recognize failed with expected return code 400 & error message and then the 2nd & 3rd recognize success
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) For first recognition request check:
                - SWIgrld: invalid grammar loaded
                - Absent events due to invalid grammar: SWIrcst, SWIrcnd, SWIrslt, NUANwvfm
            b) For 2nd & 3rd recognition requests check:
                - SWIgrld: grammar loaded
                - SWIrslt: expected recognition result, and grammar used for recognition result
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio1 = "945015260.ulaw"
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'xxxx'
        test_expect11 = "code: 400"
        test_expect12 = 'message: \"Bad Request\"'
        test_expect13 = "details: \"Failed to load RecognitionResource"
        test_recogParams1 = client.recognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)
        #
        test_audio2 = 'yes.ulaw'
        test_grammar_data2 = "uri_grammar_yes.grxml"
        test_grammar_type2 = "uri_grammar"
        test_media_type2 = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar_data2
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect2 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri, mediaType=test_media_type2)
        test_recInit2 = client.recognition_init(test_recogParams2, test_recogRes2)
        #
        test_audio3 = 'one.ulaw'
        test_grammar_data3 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>one</item>\n<item>yes</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type3 = 'inline_grammar'
        test_media_type3 = 'srgsxml'
        test_expect3 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>one</SWI_literal>.+<SWI_meaning.+one.+SWI_meaning></instance></interpretation></result>"
        test_recogParams3 = client.recognition_parameters()
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_data3, mediaType=test_media_type3)
        test_recInit3 = client.recognition_init(test_recogParams3, test_recogRes3)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect11, status_code=400, status_message="Bad Request")
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/xxxx")
        test_record_1.add_undesired_to_checklist("SWIrcst")
        test_record_1.add_undesired_to_checklist("SWIrcnd")
        test_record_1.add_undesired_to_checklist("SWIrslt")
        #test_record_1.add_undesired_to_checklist("NUANwvfm")

        test_record_2 = kafka.create_messages_record(recogInit=test_recInit2, expected_result=test_expect2)
        test_record_2.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_2.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_2.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect2)
        test_record_2.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\""+test_grammar_uri)

        test_record_3 = kafka.create_messages_record(recogInit=test_recInit3, expected_result=test_expect3)
        test_record_3.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_3.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=en-US")
        test_record_3.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect3)
        test_record_3.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"FluentD redacted possible CCN\"")

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio3, recInit=test_recInit3)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect13)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)
            #
            kafka.validate_callLogs([test_record_1, test_record_2, test_record_3])

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()
            kafka.cleanup()

    def test013_RecognitionInvalid_BuiltinThenInvalidUriGrammarThenValidInline(self):
        """
        Test NRC multiple recognition - Invalid builtin grammar recognize then Invalid Uri grammar recognize then Valid inline grammar recognize
        Expect NRC first 2 recognize failed with expected return code 400 & error message and the 3rd recognize success
        """
        client = gRPCClient()
        #
        test_audio1 = "945015260.ulaw"
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'xxxx'
        test_expect11 = "code: 400"
        test_expect12 = 'message: \"Bad Request\"'
        test_expect13 = "details: \"Failed to load RecognitionResource"

        test_recogParams1 = client.recognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)
        #
        test_audio2 = 'yes.ulaw'
        test_grammar_data2 = "xxxx.grxml"
        test_grammar_type2 = "uri_grammar"
        test_media_type2 = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar_data2
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect21 = "code: 400"
        test_expect22 = 'message: \"Bad Request\"'
        test_expect23 = "details: \"Failed to load RecognitionResource"

        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri, mediaType=test_media_type2)
        test_recInit2 = client.recognition_init(test_recogParams2, test_recogRes2)
        #
        test_audio3 = 'one.ulaw'
        test_grammar_data3 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>one</item>\n<item>yes</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type3 = 'inline_grammar'
        test_media_type3 = 'srgsxml'
        test_expect3 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>one</SWI_literal>.+<SWI_meaning.+one.+SWI_meaning></instance></interpretation></result>"

        test_recogParams3 = client.recognition_parameters()
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_data3, mediaType=test_media_type3)
        test_recInit3 = client.recognition_init(test_recogParams3, test_recogRes3)

        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio3, recInit=test_recInit3)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect13)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect21)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect22)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect23)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)

    def test014_RecognitionInvalid_BuiltinThenInvalidUriGrammarThenInvalidInline(self):
        """
        Test NRC multiple recognition - Invalid builtin grammar recognize then Invalid Uri grammar recognize then Invalid inline grammar recognize
        Expect 
        1) [Test Case] NRC 3 recognize all failed with expected return code 400 & error message
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) For every recognition request check:
                - SWIgrld: invalid grammar loaded
                - Absent events due to invalid grammar: SWIrcst, SWIrcnd, SWIrslt, NUANwvfm
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio1 = "945015260.ulaw"
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'xxxx'
        test_expect11 = "code: 400"
        test_expect12 = 'message: \"Bad Request\"'
        test_expect13 = "details: \"Failed to load RecognitionResource"
        test_recogParams1 = client.recognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)
        #
        test_audio2 = 'yes.ulaw'
        test_grammar_data2 = "xxxx.grxml"
        test_grammar_type2 = "uri_grammar"
        test_media_type2 = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar_data2
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect21 = "code: 400"
        test_expect22 = 'message: \"Bad Request\"'
        test_expect23 = "details: \"Failed to load RecognitionResource"
        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri, mediaType=test_media_type2)
        test_recInit2 = client.recognition_init(test_recogParams2, test_recogRes2)
        #
        test_audio3 = 'one.ulaw'
        test_grammar_data3 = "<?xml version=\"1.0\"?>xxxxx</grammar>\n"
        test_grammar_type3 = 'inline_grammar'
        test_media_type3 = 'srgsxml'
        test_expect31 = "code: 400"
        test_expect32 = 'message: \"Bad Request\"'
        test_expect33 = "details: \"Failed to load RecognitionResource"
        test_recogParams3 = client.recognition_parameters()
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_data3, mediaType=test_media_type3)
        test_recInit3 = client.recognition_init(test_recogParams3, test_recogRes3)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect11, status_code=400, status_message="Bad Request")
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/xxxx")
        test_record_1.add_undesired_to_checklist("SWIrcst")
        test_record_1.add_undesired_to_checklist("SWIrcnd")
        test_record_1.add_undesired_to_checklist("SWIrslt")
        #test_record_1.add_undesired_to_checklist("NUANwvfm")

        test_record_2 = kafka.create_messages_record(recogInit=test_recInit2, expected_result=test_expect21, status_code=400, status_message="Bad Request")
        test_record_2.set_checklist_types(["Basic", "Recognition", "Grammar"])
        test_record_2.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_2.add_undesired_to_checklist("SWIrcst")
        test_record_2.add_undesired_to_checklist("SWIrcnd")
        test_record_2.add_undesired_to_checklist("SWIrslt")
        #test_record_2.add_undesired_to_checklist("NUANwvfm")

        test_record_3 = kafka.create_messages_record(recogInit=test_recInit3, expected_result=test_expect31, status_code=400, status_message="Bad Request")
        test_record_3.set_checklist_types(["Basic", "Recognition", "Grammar"])
        test_record_3.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=en-US")
        test_record_3.add_undesired_to_checklist("SWIrcst")
        test_record_3.add_undesired_to_checklist("SWIrcnd")
        test_record_3.add_undesired_to_checklist("SWIrslt")
        #test_record_3.add_undesired_to_checklist("NUANwvfm")

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio3, recInit=test_recInit3)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect13)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect21)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect22)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect23)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect31)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect32)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect33)
            #
            kafka.validate_callLogs([test_record_1, test_record_2, test_record_3])

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()
            kafka.cleanup()

    def test015_RecognitionWith_No_Audio(self):
        """
        Test NRC recognition - recognize with no audio (empty.ulaw)
        Expect 
        1) [Test Case] NRC recognize fail with return code 408 and message 'no-input-timeout'
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) check:
                - SWIgrld: correct grammar loaded
                - SWIrcnd: stop to RSTT and RENR tokens
                - SWIstop: recognizer stop event due to TIMEOUT -> No speech detected; timeout.
                - Absent events: SWIrslt and NUANwvfm due to empty audio
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = "empty.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_expect1 = "code: 404"
        test_expect2 = 'message: \"No Speech\"'

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect1, status_code=404, status_message="No Speech (audio silence)")
        test_record_1.set_checklist_types(["Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="stop")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RENR", value="stop")
        test_record_1.add_token_to_checklist(evnt="SWIstop", token="MODE", value="TIMEOUT")
        test_record_1.add_undesired_to_checklist("SWIrslt")
        #test_record_1.add_undesired_to_checklist("NUANwvfm")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(5)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test016_RecognitionStartOfSpeech_ok(self):
        """
        Test NRC recognition response message StartOfSpeech - send two recognize requests separately, 1st audio '07.ulaw' with ~500ms silence at start of speech, 2nd audio 'silence1s_0124.ulaw' with ~800ms silence at start of speech
        Expect NRC recognize successful for 1st audio return first_audio_to_start_of_speech_ms ~500ms and 2nd audio return ~800ms
        """
        client = gRPCClient()
        # recognize 1 :init
        test_audio1 = "07.ulaw"
        test_audio_format1 = 'ulaw'
        test_expect11 = "first_audio_to_start_of_speech_ms: 560"
        test_expect12 = "<result><interpretation grammar=.+builtin:grammar\/digits.+instance>07</instance></interpretation>.+\</result>"
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource()
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)

        # recognize 2: init
        test_audio2 = 'silence1s_01234.ulaw'
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        test_expect21 = 'first_audio_to_start_of_speech_ms: 780'
        test_expect22 = '<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>01234<\/instance.+\/interpretation.+\/result>'
        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams2, recogRes=test_recogRes2)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect21)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect22)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test017_RecognitionStartOfSpeech_empty(self):
        """
        Test NRC recognition response message StartOfSpeech - send two recognize requests with 2 audio very small silence at start of speech, 1st audio '01234.ulaw', 2nd audio 'one.ulaw'
        Expect NRC recognize successful for 1st and 2nd audio return empty for first_audio_to_start_of_speech_ms
        """
        client = gRPCClient()
        # recognize 1 :init
        test_audio1 = "01234.ulaw"
        test_audio_format1 = 'ulaw'
        test_expect11 = "start_of_speech return: first_audio_to_start_of_speech_ms: 0"
        test_expect12 = "<result><interpretation grammar=.+builtin:grammar\/digits.+instance>01234</instance></interpretation>.+\</result>"
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource()
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)

        # recognize 2: init
        test_audio2 = '1.ulaw'
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        test_expect21 = 'start_of_speech return: first_audio_to_start_of_speech_ms: 0'  # return for first_audio_to_end_of_speech_ms
        test_expect22 = '<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>'
        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams2, recogRes=test_recogRes2)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect21)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect22)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test018_RecognitionEndOfSpeech_ok(self):
        """
        Test NRC recognition response message EndOfSpeech - send two recognize requests separately, 1st audio '07.ulaw' with ~2800ms silence at end of speech, 2nd audio 'silence1s_0124.ulaw' with ~3800ms silence at end of speech
        Expect 
        1) [Test Case] NRC recognize successful for 1st audio return first_audio_to_end_of_speech_ms is ~2800ms and 2nd audio return ~3800ms
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        # recognize 1 :init
        test_audio1 = "07.ulaw"
        test_audio_format1 = 'ulaw'
        test_expect11 = "end_of_speech return: first_audio_to_end_of_speech_ms: 2885"
        test_expect12 = "<result><interpretation grammar=.+builtin:grammar\/digits.+instance>07</instance></interpretation>.+\</result>"
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource()
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)

        # recognize 2: init
        test_audio2 = 'silence1s_01234.ulaw'
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        test_expect21 = 'end_of_speech return: first_audio_to_end_of_speech_ms: 3796'
        test_expect22 = '<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>01234<\/instance.+\/interpretation.+\/result>'
        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams2, recogRes=test_recogRes2)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect12)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect12)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        test_record_2 = kafka.create_messages_record(recogInit=test_recInit2, expected_result=test_expect22)
        test_record_2.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_2.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_2.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect22)
        test_record_2.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect21)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect22)
            #
            kafka.validate_callLogs([test_record_1, test_record_2])

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test019_RecognitionEndOfSpeech_endsilence(self):
        """
        Test NRC recognition response message EndOfSpeech - send two recognize requests separately, 1st audio '0123_no-end-silence.ulaw' with no silence at end of speech, 2nd audio '0123.ulaw' same audio but with silence at end of speech
        Expect 
        1) [Test Case] NRC recognize successful for 1st audio return first_audio_to_end_of_speech_ms is ~1600ms which no end silence and 2nd audio return ~2300ms with silence at end of speech
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        # recognize 1 :init
        test_audio1 = "0123_no-end-silence.ulaw"
        test_audio_format1 = 'ulaw'
        test_expect11 = "end_of_speech return: first_audio_to_end_of_speech_ms: 1671"
        test_expect12 = "<result><interpretation grammar=.+builtin:grammar\/digits.+instance>0123</instance></interpretation>.+\</result>"
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource()
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)

        # recognize 2: init
        test_audio2 = '0123.ulaw'
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        test_expect21 = 'end_of_speech return: first_audio_to_end_of_speech_ms: 2325'
        test_expect22 = "<result><interpretation grammar=.+builtin:grammar\/digits.+instance>0123</instance></interpretation>.+\</result>"
        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams2, recogRes=test_recogRes2)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect12)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect12)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        test_record_2 = kafka.create_messages_record(recogInit=test_recInit2, expected_result=test_expect22)
        test_record_2.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_2.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_2.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect22)
        test_record_2.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect21)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect22)
            #
            kafka.validate_callLogs([test_record_1, test_record_2])
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()
            kafka.cleanup()

    def test020_RecognitionWith_Noise_Audio(self):
        """
        Test NRC recognition with noise audio input, 1st audio high noise volume 'noise_high.ulaw', 2nd audio low noise volume 'noise_low.ulaw'
        Expect 
        1) [Test Case] NRC recognize fail for both 1st & 2nd noise audio input with return error code 408 message 'No-input Timeout'
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) check:
                - SWIgrld: correct grammar loaded
                - SWIrcnd: stop to RSTT and RENR tokens
                - SWIstop: recognizer stop event due to TIMEOUT -> No speech detected; timeout.
                - Absent events: SWIrslt and NUANwvfm due to empty audio
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        # recognize 1 :init
        test_audio1 = "noise_high.ulaw"
        test_audio_format1 = 'ulaw'
        test_expect11 = "code: 404"
        test_expect12 = "message: \"No Speech\""
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource()
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)

        # recognize 2: init
        test_audio2 = 'noise_low.ulaw'
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        test_expect21 = "code: 404"
        test_expect22 = "message: \"No Speech\""
        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams2, recogRes=test_recogRes2)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect12, status_message="No Speech (audio silence)", status_code=404)
        test_record_1.set_checklist_types(["Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="stop")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RENR", value="stop")
        test_record_1.add_token_to_checklist(evnt="SWIstop", token="MODE", value="TIMEOUT")
        test_record_1.add_undesired_to_checklist("SWIrslt")
        #test_record_1.add_undesired_to_checklist("NUANwvfm")

        test_record_2 = kafka.create_messages_record(recogInit=test_recInit2, expected_result=test_expect22, status_message="No Speech (audio silence)", status_code=404)
        test_record_2.set_checklist_types(["Recognition", "Grammar", "Endpointer"])
        test_record_2.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_2.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="stop")
        test_record_2.add_token_to_checklist(evnt="SWIrcnd", token="RENR", value="stop")
        test_record_2.add_token_to_checklist(evnt="SWIstop", token="MODE", value="TIMEOUT")
        test_record_2.add_undesired_to_checklist("SWIrslt")
        #test_record_2.add_undesired_to_checklist("NUANwvfm")

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect21)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect22)
            #
            kafka.validate_callLogs([test_record_1, test_record_2])
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test500_RecognitionUriGrammarThenInlineGrammarThenBuiltin_Silence(self):
        """
        Test NRC multiple recognition - Uri grammar, then Inline grammar, then builtin grammar with audio "silence.ulaw"
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio1 = "silence.ulaw"
        test_grammar_data1 = "uri_grammar_yes.grxml"
        test_grammar_type1 = "uri_grammar"
        test_media_type1 = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar_data1

        test_recogParams1 = client.recognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)
        #
        test_audio2 = "silence.ulaw"
        test_grammar_data2 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>one</item>\n<item>yes</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type2 = 'inline_grammar'
        test_media_type2 = 'srgsxml'

        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2, mediaType=test_media_type2)
        test_recInit2 = client.recognition_init(test_recogParams2, test_recogRes2)
        #
        test_audio3 = "silence.ulaw"
        test_grammar_type3 = 'builtin'
        test_grammar_data3 = 'digits'

        test_recogParams3 = client.recognition_parameters()
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_data3)
        test_recInit3 = client.recognition_init(test_recogParams3, test_recogRes3)
        #
        test_expect1 = 'code: 404'
        test_expect2 = 'message: \"No Speech\"'
        test_expect3 = 'details: \"No speech detected\"'
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio3, recInit=test_recInit3)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            self.debug(msg)
            print(msg)    # for debug

            # Validate result 1
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect3)

            # Validate result 2
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)

            # Validate result 3
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect2)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test501_RecognitionUriGrammarThenInlineGrammarThenBuiltin_No_Audio(self):
        """
        Test NRC multiple recognition - Uri grammar, then Inline grammar, then builtin grammar with audio "empty.ulaw"
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio1 = "empty.ulaw"
        test_grammar_data1 = "uri_grammar_yes.grxml"
        test_grammar_type1 = "uri_grammar"
        test_media_type1 = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar_data1

        test_recogParams1 = client.recognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)
        #
        test_audio2 = "empty.ulaw"
        test_grammar_data2 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>one</item>\n<item>yes</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type2 = 'inline_grammar'
        test_media_type2 = 'srgsxml'

        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2, mediaType=test_media_type2)
        test_recInit2 = client.recognition_init(test_recogParams2, test_recogRes2)
        #
        test_audio3 = "empty.ulaw"
        test_grammar_type3 = 'builtin'
        test_grammar_data3 = 'digits'

        test_recogParams3 = client.recognition_parameters()
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_data3)
        test_recInit3 = client.recognition_init(test_recogParams3, test_recogRes3)
        #
        test_expect1 = 'code: 404'
        test_expect2 = 'message: \"No Speech\"'
        test_expect3 = 'details: \"No speech detected\"'
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio3, recInit=test_recInit3)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            self.debug(msg)
            print(msg)    # for debug

            # Validate result 1
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect3)

            # Validate result 2
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)

            # Validate result 3
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect2)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test502_RecognitionUriGrammarThenInlineGrammarThenBuiltin_Noise_Audio(self):
        """
        Test NRC multiple recognition - Uri grammar, then Inline grammar, then builtin grammar with audio "noise_high.ulaw"
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio1 = "noise_high.ulaw"
        test_grammar_data1 = "uri_grammar_yes.grxml"
        test_grammar_type1 = "uri_grammar"
        test_media_type1 = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar_data1

        test_recogParams1 = client.recognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)
        #
        test_audio2 = "noise_high.ulaw"
        test_grammar_data2 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>one</item>\n<item>yes</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type2 = 'inline_grammar'
        test_media_type2 = 'srgsxml'

        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2, mediaType=test_media_type2)
        test_recInit2 = client.recognition_init(test_recogParams2, test_recogRes2)
        #
        test_audio3 = "noise_high.ulaw"
        test_grammar_type3 = 'builtin'
        test_grammar_data3 = 'digits'

        test_recogParams3 = client.recognition_parameters()
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_data3)
        test_recInit3 = client.recognition_init(test_recogParams3, test_recogRes3)
        #
        test_expect1 = 'code: 404'
        test_expect2 = 'message: \"No Speech\"'
        test_expect3 = 'details: \"No speech detected\"'
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio3, recInit=test_recInit3)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            self.debug(msg)
            print(msg)    # for debug

            # Validate result 1
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect3)

            # Validate result 2
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)

            # Validate result 3
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect2)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test503_RecognitionDtmf_enUSThenesUSThenfrCA(self):
        client = gRPCClient()

        test_dtmf = '20*00'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'currency'
        test_recogParams = client.dtmfrecognition_parameters()

        test_language1 = 'en-US'
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language1)
        test_dtmfrecInit1 = client.dtmfrecognition_init(test_recogParams, test_recogRes1)
        test_expect1 = "<result><interpretation grammar=.+builtin:dtmf\/currency.+<instance>USD20.00<\/instance.+\/interpretation.+\/result>"

        test_language2 = 'es-US'
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language2)
        test_dtmfrecInit2 = client.dtmfrecognition_init(test_recogParams, test_recogRes2)
        test_expect2 = "<result><interpretation grammar=.+builtin:dtmf\/currency.+<instance>20.00<\/instance.+\/interpretation.+\/result>"

        test_language3 = 'fr-CA'
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language3)
        test_dtmfrecInit3 = client.dtmfrecognition_init(test_recogParams, test_recogRes3)
        test_expect3 = "<result><interpretation grammar=.+builtin:dtmf\/currency.+<instance>20.00<\/instance.+\/interpretation.+\/result>"
        try:
            test_result1 = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit3)
            time.sleep(1)

            msg = "Test result1:\n" + test_result1 + "\n"
            msg += "Test result2:\n" + test_result2 + "\n"
            msg += "Test result3:\n" + test_result3 + "\n"
            self.debug(msg)
            print(msg)  # for debug 
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test504_RecognitionAudio_enUSThenesUSThenfrCA(self):
        client = gRPCClient()
        
        test_language1 = "en-US"
        test_audio1 = "c375037503750373_8KHz.wav"
        test_audio_format1 = 'pcm'
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)        
        test_recogRes1 = client.recognition_resource(grammarType='builtin', grammarData='digits', languageIn=test_language1)
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>375037503750373<\/instance.+\/interpretation.+\/result>"
        
        test_language2 = "es-US"
        test_audio2 = '1234_es.ulaw'
        test_audio_format2 = 'ulaw'
        test_recogParams2 = client.recognition_parameters(audioFormat=test_audio_format2)        
        test_recogRes2 = client.recognition_resource(grammarType='builtin', grammarData='digits', languageIn=test_language2)
        test_recInit2 = client.recognition_init(test_recogParams2, test_recogRes2)
        test_expect2 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>1234<\/instance.+\/interpretation.+\/result>"
        
        test_language3 = "fr-CA"
        test_audio3 = '1234_fr.ulaw.raw'
        test_audio_format3 = 'ulaw'
        test_recogParams3 = client.recognition_parameters(audioFormat=test_audio_format3)
        test_recogRes3 = client.recognition_resource(grammarType='builtin', grammarData='digits', languageIn=test_language3)
        test_recInit3 = client.recognition_init(test_recogParams3, test_recogRes3)
        test_expect3 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>1234<\/instance.+\/interpretation.+\/result>"
        
        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio3, recInit=test_recInit3)
            time.sleep(1)
            
            msg = "Test result1:\n" + test_result1 + "\n"
            msg += "Test result2:\n" + test_result2 + "\n"
            msg += "Test result3:\n" + test_result3 + "\n"

            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
