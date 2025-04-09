import sys
import os
import time

from Framework.nrctest.NRCSetupClass.TestFixture import TestFixture
from Framework.nrctest.NRCSetupClass.gRPCClient import gRPCClient, TimeoutException
from Framework.nrctest.NRCSetupClass.KafkaModule import KafkaModule

if os.path.isdir(os.path.join(os.path.dirname(__file__), '../../', './NRCSetupClass')):
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../', './NRCSetupClass'))
else:
    raise ImportError("No Such path to the NRCSetup Class")

# ------- NRC automation test class -----------
class NRCTestRecognitionParams(TestFixture):
    """ NRC Recognition Parameters test"""

    def test001_RecogParamGeneric1(self):
        """
        Test NRC recognition parameters generic 1 - recognition parameters API with default parameter & config
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio = None
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_expect = "<result>.+\/result>"
        #
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test002_RecogResultFormatNLSML(self):
        """
        Test NRC recognition parameters - result_format - NLSML
        Expect 
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = "one.ulaw"
        test_audio_format = 'ulaw'
        test_result_format = 'nlsml'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format, resultFormat=test_result_format)
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar\/digits")
        test_record_1.add_event_to_checklist(event="EVNT", value="SWIacum")
        test_record_1.add_token_to_checklist(evnt="SWIliss", token="LFEAT", value="osr_rec_tier4")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(3)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test003_RecogResultFormatEMMA(self):
        """
        Test NRC recognition parameters - result_format - EMMA
        Expect 
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = "one.ulaw"
        test_audio_format = 'ulaw'
        test_result_format = 'emma'
        test_expect = "<?xml.+<emma:emma.+<emma:interpretation.+emma:tokens=.+one.+emma:interpretation>.+emma:emma>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format, resultFormat=test_result_format)
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIliss", token="LFEAT", value="osr_rec_tier4")
        test_record_1.add_event_to_checklist(event="EVNT", value="SWIacum")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="MEDIA", value="application/x-vnd.nuance.emma+xml")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(3)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test004_RecognitionRepeatedResourceGrammar_BuiltinAndInlineGrammar(self):
        """
        Test NRC recognition with init & load repeated resource grammars - builtins and Inline grammar, next recognize audio 945015260.ulaw then yes.ulaw
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio1 = "945015260.ulaw"
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)

        test_audio2 = 'yes.ulaw'
        test_grammar_data2 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>one</item>\n<item>yes</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type2 = 'inline_grammar'
        test_media_type2 = 'srgsxml'
        test_expect2 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation>.+</result>"
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2,
                                                     mediaType=test_media_type2)

        test_recogParams = client.recognition_parameters()
        test_recogRes = [test_recogRes1, test_recogRes2]
        # test_recogRes.extend(test_recogRes2)
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test005_RecognitionRepeatedResourceGrammar_BuiltinAndUriGrammar(self):
        """
        Test NRC recognition with init & load repeated resource grammars - builtins and Uri-grammar, next recognize audio 945015260.ulaw then yes.ulaw
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio1 = "945015260.ulaw"
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)

        test_audio2 = 'yes.ulaw'
        test_grammar_data2 = "uri_grammar_yes.grxml"
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_grammar_type2 = 'uri_grammar'
        test_media_type2 = 'srgsxml'
        test_expect2 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation>.+</result>"
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,
                                                     mediaType=test_media_type2)

        test_recogParams = client.recognition_parameters()
        test_recogRes = [test_recogRes1, test_recogRes2]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test006_RecognitionRepeatedResourceGrammar_InlineAndUriGrammar(self):
        """
        Test NRC recognition with init & load repeated resource grammars - Inline grammar and Uri-grammar, next recognize audio one.ulaw then yes.ulaw
        Expect 
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
                Check SWIgrld respective to each grammar appear in order and the correct grammar is used in each recognition request
            Note: each recognition request corresponds to one messages record for the call logging automation testing
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio1 = 'one.ulaw'
        test_grammar_data1 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_one\"> <rule id=\"yes_one\" scope=\"public\">\n<one-of>\n<item>one</item>\n<item>yes</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type1 = 'inline_grammar'
        test_media_type1 = 'srgsxml'
        test_expect1 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>one</SWI_literal>.+<SWI_meaning.+one.+SWI_meaning></instance></interpretation>.+</result>"
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1, mediaType=test_media_type1)

        test_audio2 = 'yes.ulaw'
        test_grammar_data2 = "uri_grammar_yes.grxml"
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_grammar_type2 = 'uri_grammar'
        test_media_type2 = 'srgsxml'
        test_expect2 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation>.+</result>"
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2, mediaType=test_media_type2)

        test_recogParams = client.recognition_parameters()
        test_recogRes = [test_recogRes1, test_recogRes2]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="TYPE", value="string")
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri2)
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect1)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"FluentD redacted possible CCN\"")

        test_record_2 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect2)
        test_record_2.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_2.add_sequence_to_checklist([test_check1, test_check2])
        test_record_2.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect2)
        test_record_2.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\""+test_grammar_uri2)

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(4)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit)
            time.sleep(4)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            self.debug(msg)
            print(msg)  # for debug
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

    def test007_RecognitionRepeatedResourceGrammar_InlineAndUriGrammarAndBuiltin(self):
        """
        Test NRC recognition with init & load repeated resource grammars - Builtins, Inline grammar and Uri-grammar, next recognize with audio one.ulaw then yes.ulaw then 945015260.ulaw
        Expect 
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
                Check SWIgrld respective to each grammar appear in order and the correct grammar is used in each recognition request
            Note: each recognition request corresponds to one messages record for the call logging automation testing
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio1 = 'one.ulaw'
        test_grammar_data1 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_one\"> <rule id=\"yes_one\" scope=\"public\">\n<one-of>\n<item>one</item>\n<item>yes</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type1 = 'inline_grammar'
        test_media_type1 = 'srgsxml'
        test_expect1 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>one</SWI_literal>.+<SWI_meaning.+one.+SWI_meaning></instance></interpretation>.+</result>"
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1, mediaType=test_media_type1)

        test_audio2 = 'yes.ulaw'
        test_grammar_data2 = "uri_grammar_yes.grxml"
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_grammar_type2 = 'uri_grammar'
        test_media_type2 = 'srgsxml'
        test_expect2 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation>.+</result>"
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2, mediaType=test_media_type2)

        test_audio3 = "945015260.ulaw"
        test_grammar_type3 = 'builtin'
        test_grammar_data3 = 'digits'
        test_expect3 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_data3)

        test_recogParams = client.recognition_parameters()
        test_recogRes = [test_recogRes1, test_recogRes2, test_recogRes3]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="TYPE", value="string")
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri2)
        test_check3 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar\/digits")
        test_record_1.add_sequence_to_checklist([test_check1, test_check2, test_check3])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect1)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"FluentD redacted possible CCN\"")

        test_record_2 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect2)
        test_record_2.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_2.add_sequence_to_checklist([test_check1, test_check2, test_check3])
        test_record_2.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect2)
        test_record_2.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\""+test_grammar_uri2)
        
        test_record_3 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect3)
        test_record_3.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_3.add_sequence_to_checklist([test_check1, test_check2, test_check3])
        test_record_3.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect3)
        test_record_3.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio3, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            self.debug(msg)
            print(msg)  # for debug
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

    def test008_Recognition_nBest_1(self):
        """
        Test NRC recognition with nBest set to 1 (confidence level set to 0 always recongize) - recognize audio voicenospeech_short.ulaw
        Expect 
        1) [Test Case] NRC recognize successfully return nBest 1 (interpretation)
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check SWIrcnd has token NBST=1
            b) Check SWIrslt contains expected recognition result and grammar used 
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio1 = 'voicenospeech_short.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_nBest1 = 1
        test_confLevel = 0  # set it to 0, which always sets the result status to success providing that Recognizer was able to populate the n-best list.

        test_expect1 = "<?xml.+<result><interpretation.+confidence=.+<instance.+/instance></interpretation></result>"
        test_recogParams1 = client.recognition_parameters(confLevel=test_confLevel, nBest=test_nBest1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="NBST", value=test_nBest1)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect1)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            #
            kafka.validate_callLogs(test_record_1)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()
            kafka.cleanup()

    def test009_Recognition_nBest_2(self):
        """
        Test NRC recognition with nBest set to 2 (confidence level set to 0 always recongize) - recognize audio voicenospeech_short.ulaw
        Expect 
        1) [Test Case] NRC recognize successfully return nBest 2 (interpretation)
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check SWIrcnd has token NBST=2
            b) Check SWIrslt contains expected recognition result and grammar used 
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio1 = 'voicenospeech_short.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_nBest1 = 2
        test_confLevel = 0  # set it to 0, which always sets the result status to success providing that Recognizer was able to populate the n-best list.

        test_expect1 = "<?xml.+<result><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation></result>"
        test_recogParams1 = client.recognition_parameters(confLevel=test_confLevel, nBest=test_nBest1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="NBST", value=test_nBest1)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect1)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            #
            kafka.validate_callLogs(test_record_1)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test010_Recognition_nBest_3(self):
        """
        Test NRC recognition with nBest set to 3 (confidence level set to 0 always recongize) - recognize audio voicenospeech_short.ulaw
        Expect NRC recognize successfully return nBest 3 (interpretation)
        """
        client = gRPCClient()
        #
        test_audio1 = 'voicenospeech_short.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_nBest1 = 3
        test_confLevel = 0  # set it to 0, which always sets the result status to success providing that Recognizer was able to populate the n-best list.

        test_expect1 = "<?xml.+<result><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation></result>"
        test_recogParams1 = client.recognition_parameters(confLevel=test_confLevel, nBest=test_nBest1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test011_Recognition_nBest_5(self):
        """
        Test NRC recognition with nBest set to 5 (confidence level set to 0 always recongize) - recognize audio voicenospeech_short.ulaw
        Expect 
        1) [Test Case] NRC recognize successfully return nBest 5 (interpretation)
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check SWIrcnd has token NBST=5
            b) Check SWIrslt contains expected recognition result and grammar used
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio1 = 'voicenospeech_short.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_nBest1 = 5
        test_confLevel = 0  # set it to 0, which always sets the result status to success providing that Recognizer was able to populate the n-best list.

        test_expect1 = "<?xml.+<result><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation></result>"
        test_recogParams1 = client.recognition_parameters(confLevel=test_confLevel, nBest=test_nBest1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="NBST", value=test_nBest1)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect1)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            #
            kafka.validate_callLogs(test_record_1)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test012_Recognition_nBest_6(self):
        """
        Test NRC recognition with nBest set to 6 (confidence level set to 0 always recongize) - recognize audio voicenospeech_short.ulaw
        Expect NRC recognize successfully return nBest 6 (interpretation)
            Note: For QA nBest test audio 'voicenospeech_short.ulaw', NRC only can return max nBest result 6. It is by design from NR swirec_nbest_list_length param see: http://mtl-repo.nuance.com/nasr/techdoc/doc_builds/SpeechSuite/html/nr_config/cfg_param_swirec_nbest_list_length.html#aanchor272
        """
        client = gRPCClient()
        #
        test_audio1 = 'voicenospeech_short.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_nBest1 = 6
        test_confLevel = 0  # set it to 0, which always sets the result status to success providing that Recognizer was able to populate the n-best list.

        test_expect1 = "<?xml.+<result><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation></result>"
        test_recogParams1 = client.recognition_parameters(confLevel=test_confLevel, nBest=test_nBest1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test013_Recognition_nBest_0(self):
        """
        Test NRC recognition with nBest set to 0 (confidence level set to 0 always recongize) - recognize audio voicenospeech_short.ulaw
        Note: For QA nBest test audio 'voicenospeech_short.ulaw', NRC only can return max nBest result 6. It is by design from NR swirec_nbest_list_length param see: http://mtl-repo.nuance.com/nasr/techdoc/doc_builds/SpeechSuite/html/nr_config/cfg_param_swirec_nbest_list_length.html#aanchor272
        Expect 
        1) [Test Case] NRC recognize successfully return nBest 0 (interpretation)
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check SWIrcnd has token NBST=0
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_nBest1 = 0
        test_confLevel = 0  # set it to 0, which always sets the result status to success providing that Recognizer was able to populate the n-best list.

        test_expect1 = "<?xml.+<result><interpretation><input><nomatch/></input><instance/></interpretation></result>"
        test_recogParams1 = client.recognition_parameters(confLevel=test_confLevel, nBest=test_nBest1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Recognition", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="NBST", value=test_nBest1)
        test_record_1.add_expression_to_checklist(test_expect1)

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            #
            kafka.validate_callLogs(test_record_1)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test014_Recognition_nBest_EMMA(self):
        """
        Test NRC recognition with nBest set to 4 and return result format as EMMA - recognize audio voicenospeech_short.ulaw
        Expect 
        1) [Test Case] NRC recognize successfully return nBest 4 EMMA result
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check SWIrcnd has token NBST=4
            b) Check SWIrslt contains expected recognition result and grammar used 
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio1 = 'voicenospeech_short.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_resultFormat1 = 'EMMA'
        test_nBest1 = 4
        test_confLevel = 0

        test_expect1 = "<?xml.+<emma:emma.+<emma:interpretation.+emma:tokens=.+emma:interpretation><emma:interpretation.+emma:tokens=.+emma:interpretation><emma:interpretation.+emma:tokens=.+emma:interpretation><emma:interpretation.+emma:tokens=.+emma:interpretation>.+emma:emma>"

        test_recogParams1 = client.recognition_parameters(confLevel=test_confLevel, nBest=test_nBest1, resultFormat=test_resultFormat1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="NBST", value=test_nBest1)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect1)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="builtin:grammar/digits")

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            #
            kafka.validate_callLogs(test_record_1)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test015_Recognition_nBest_NLSML(self):
        """
        Test NRC recognition with nBest set to 4 and return result format as NLSML - recognize audio voicenospeech_short.ulaw
        Expect 
        1) [Test Case] NRC recognize successfully return nBest 4 NLSML result
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check SWIrcnd has token NBST=4
            b) Check SWIrslt contains expected recognition result and grammar used 
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio1 = 'voicenospeech_short.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_resultFormat1 = 'NLSML'
        test_nBest1 = 4
        test_confLevel = 0

        test_expect1 = "<?xml.+<result><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation></result>"

        test_recogParams1 = client.recognition_parameters(confLevel=test_confLevel, nBest=test_nBest1, resultFormat=test_resultFormat1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="NBST", value=test_nBest1)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect1)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            #
            kafka.validate_callLogs(test_record_1)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test016_Recognition_confLevel_allaccepted(self):
        """
        Test NRC recognition with confidence_level set to 0 (all utterance inputs accepted) - recognize audio (noise) no_match.ulaw & voicenospeech_short.ulaw
        Expect NRC recognize successfully return for both utterances
        """
        client = gRPCClient()
        # recognize 1 :init
        test_audio1 = 'no_match.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_nBest1 = 1
        test_confLevel1 = 0  # set it to 0, which always sets the result status to success providing that Recognizer was able to populate the n-best list.
        test_expect1 = "<?xml.+<result><interpretation.+confidence=.+<instance.+/instance></interpretation></result>"
        test_recogParams1 = client.recognition_parameters(confLevel=test_confLevel1, nBest=test_nBest1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)

        # recognize 2: init
        test_audio2 = 'voicenospeech_short.ulaw'
        test_grammar_type2 = 'inline_grammar'
        test_grammar_data2 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type2 = 'srgsxml'
        test_nBest2 = 1
        test_confLevel2 = 0
        test_expect2 = "<?xml.+<result><interpretation.+confidence=.+<instance.+/instance></interpretation></result>"
        test_recogParams2 = client.recognition_parameters(confLevel=test_confLevel2, nBest=test_nBest2)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2, mediaType=test_media_type2)
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
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test017_Recognition_confLevel_low(self):
        """
        Test NRC recognition with confidence_level set to 0.2 (low) - recognize audio (no_match.ulaw) ok then with confidence_level set to 0.5 (medium) recognize failed
        Expect 
        1) [Test Case] NRC recognize successfully return 1st one ok, 2nd one SWIrec_STATUS_NO_MATCH
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Recognition Request 1:
                Check NBEST=1
                Check SWIrslt contains expected recognition result and confidence inside range [20,99]
            b) Recognition Request 2: 
                Check SWIrcnd contains return code RSTT=lowconf (n-best result below confidencelevel)
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        # recognize 1 :init
        test_audio1 = 'no_match.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_nBest1 = 1
        test_confLevel1 = 0.2  # set it to 0, which always sets the result status to success providing that Recognizer was able to populate the n-best list.
        test_expect1 = "<?xml.+<result><interpretation.+confidence=.+<instance.+/instance></interpretation></result>"
        test_recogParams1 = client.recognition_parameters(confLevel=test_confLevel1, nBest=test_nBest1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)

        # recognize 2: init
        test_confLevel2 = 0.5
        #test_expect2 = "SWIrec_STATUS_NO_MATCH"
        test_expect2 = "NO_MATCH"
        #test_expect2 =  "<result>.*nomatch.*/result>"
        test_recogParams2 = client.recognition_parameters(confLevel=test_confLevel2, nBest=test_nBest1)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams2, recogRes=test_recogRes2)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="NBST", value=test_nBest1)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect1)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="confidence=.+[2-9][0-9]+") # verify confidence inside range [20,99]

        test_record_2 = kafka.create_messages_record(recogInit=test_recInit2, expected_result=test_expect2, result_status="NO_MATCH")
        test_record_2.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_2.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="lowconf")
        test_record_2.add_undesired_to_checklist("SWIrslt")


        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(5)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit2)
            time.sleep(5)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            self.debug(msg)
            print(msg)  # for debug
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

    def test018_Recognition_confLevel_high(self):
        """
        Test NRC recognition with confidence_level set to 0.5 (medium) - recognize audio (yes.ulaw) ok then set confidence_level to 0.9 (high) recognize failed
        Expect 
        1) [Test Case] NRC recognize successfully return 1st one ok, 2nd one SWIrec_STATUS_NO_MATCH
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Recognition Request 1:
                Check NBEST=1
                Check SWIrslt contains expected recognition result and confidence inside range [50,99]
            b) Recognition Request 2: 
                Check SWIrcnd contains return code RSTT=lowconf (n-best result below confidencelevel)
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        # recognize 1 :init
        test_audio1 = 'yes.ulaw'
        test_grammar_data1 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type1 = 'srgsxml'
        test_grammar_type1 = 'inline_grammar'
        test_nBest1 = 1
        test_confLevel1 = 0.5  # set it to 0, which always sets the result status to success providing that Recognizer was able to populate the n-best list.
        test_expect1 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        test_recogParams1 = client.recognition_parameters(confLevel=test_confLevel1, nBest=test_nBest1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1, mediaType=test_media_type1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)

        # recognize 2: init
        test_confLevel2 = 0.9  # set it to 0, which always sets the result status to success providing that Recognizer was able to populate the n-best list.
        #test_expect2 = "SWIrec_STATUS_NO_MATCH"
        #test_expect2 =  "<result>.*nomatch.*/result>"
        test_expect2 = "NO_MATCH"
        test_recogParams2 = client.recognition_parameters(confLevel=test_confLevel2, nBest=test_nBest1)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1, mediaType=test_media_type1)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams2, recogRes=test_recogRes2)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="NBST", value=test_nBest1)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect1)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="confidence=.+[5-9][0-9]+") # verify confidence inside range [20,99]

        test_record_2 = kafka.create_messages_record(recogInit=test_recInit2, expected_result=test_expect2, result_status="NO_MATCH")
        test_record_2.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_2.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="lowconf")
        test_record_2.add_undesired_to_checklist("SWIrslt")

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(3)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit2)
            time.sleep(3)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            self.debug(msg)
            print(msg)  # for debug
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

    def test019_Recognition_confLevel_allnomatch(self):
        """
        Test NRC recognition with confidence_level set to 1.0 (all utterance inputs not accepted no-match) - recognize audio one.ulaw & yes.ulaw
        Expect 
        1) [Test Case] NRC recognize return SWIrec_STATUS_NO_MATCH for both utterances
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            For both Recognition Requests, check SWIrcnd contains return code RSTT=lowconf (n-best result below confidencelevel)
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        # recognize 1 :init
        test_audio1 = 'one.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_nBest1 = 1
        test_confLevel1 = 1.0  # set it to 0, which always sets the result status to success providing that Recognizer was able to populate the n-best list.
        #test_expect1 = "SWIrec_STATUS_NO_MATCH"
        test_expect1 = "NO_MATCH"
        #test_expect1 =  "<result>.*nomatch.*/result>"
        test_recogParams1 = client.recognition_parameters(confLevel=test_confLevel1, nBest=test_nBest1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)

        # recognize 2: init
        test_audio2 = 'yes.ulaw'
        test_grammar_type2 = 'inline_grammar'
        test_grammar_data2 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type2 = 'srgsxml'
        test_nBest2 = 1
        test_confLevel2 = 1.0
        #test_expect2 = "SWIrec_STATUS_NO_MATCH"
        test_expect2 = "NO_MATCH"
        #test_expect2 =  "<result>.*nomatch.*/result>"
        test_recogParams2 = client.recognition_parameters(confLevel=test_confLevel2, nBest=test_nBest2)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2, mediaType=test_media_type2)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams2, recogRes=test_recogRes2)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1, result_status="NO_MATCH")
        test_record_1.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="lowconf")
        test_record_1.add_undesired_to_checklist("SWIrslt")

        test_record_2 = kafka.create_messages_record(recogInit=test_recInit2, expected_result=test_expect2, result_status="NO_MATCH")
        test_record_2.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_2.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="lowconf")
        test_record_2.add_undesired_to_checklist("SWIrslt")

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(3)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(3)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            self.debug(msg)
            print(msg)  # for debug
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

    def test020_Recognition_no_input_timeout_disabled(self):
        """
        Test NRC recognition parameter no_input_timeout_ms set to -1 (no timeout, disabled) - recognize '945015260.ulaw' &  'yes.ulaw'
        Expect NRC recognize success for both utterances
        """
        client = gRPCClient()
        # recognize 1 :init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_noInputTimeout1 = -1
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"
        test_recogParams1 = client.recognition_parameters(noInputTimeout=test_noInputTimeout1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)

        # recognize 2: init
        test_audio2 = 'yes.ulaw'
        test_grammar_type2 = 'inline_grammar'
        test_grammar_data2 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type2 = 'srgsxml'
        test_noInputTimeout2 = -1
        test_expect2 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        test_recogParams2 = client.recognition_parameters(noInputTimeout=test_noInputTimeout2)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2, mediaType=test_media_type2)
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
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test021_Recognition_no_input_timeout_invalid(self):
        """
        Test NRC recognition parameter no_input_timeout_ms set to -2 & -3  (not allowed, invalid value) - recognize '945015260.ulaw' &  'yes.ulaw'
        Expect NRC recognize return code 400 (bad requests) for both invalid settings
        """
        client = gRPCClient()
        # recognize 1 :init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_noInputTimeout1 = -3
        test_expect11 = "code: 400"
        test_expect12 = 'message: \"Bad Request\"'
        test_expect13 = 'details: \"The no_input_timeout_ms parameter is out of range.+\"'
        test_recogParams1 = client.recognition_parameters(noInputTimeout=test_noInputTimeout1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)

        # recognize 2: init
        test_audio2 = 'yes.ulaw'
        test_grammar_type2 = 'inline_grammar'
        test_grammar_data2 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type2 = 'srgsxml'
        test_noInputTimeout2 = -2
        test_expect21 = "code: 400"
        test_expect22 = 'message: \"Bad Request\"'
        test_expect23 = 'details: \"The no_input_timeout_ms parameter is out of range.+\"'
        test_recogParams2 = client.recognition_parameters(noInputTimeout=test_noInputTimeout2)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2, mediaType=test_media_type2)
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
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect13)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect21)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect22)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect23)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test022_Recognition_no_input_timeout_always(self):
        """
        Test NRC recognition parameter no_input_timeout_ms set to 0 (always timeout)  - recognize 'yes.ulaw'
        Expect NRC recognize return no-input timeout with code 404 for both cases
        """
        client = gRPCClient()
        # recognize 1 :init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_noInputTimeout1 = 0
        test_expect11 = "code: 404"
        test_expect12 = 'message: \"No Speech\"'
        test_recogParams1 = client.recognition_parameters(noInputTimeout=test_noInputTimeout1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)

        # recognize 2: init
        test_audio2 = 'yes.ulaw'
        test_grammar_type2 = 'inline_grammar'
        test_grammar_data2 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type2 = 'srgsxml'
        test_noInputTimeout2 = 0
        test_expect21 = "code: 404"
        test_expect22 = 'message: \"No Speech\"'
        test_recogParams2 = client.recognition_parameters(noInputTimeout=test_noInputTimeout2)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2, mediaType=test_media_type2)
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

    def test023_Recognition_no_input_timeout_ok(self):
        """
        Test NRC recognition parameter no_input_timeout_ms set to 500ms and then 1200ms - recognize separately with same audio with 1000ms silence 'silence1s_01234.ulaw'
        Expect 
        1) [Test Case] NRC recognize return no-input timeout for 1st case and passed for 2nd case
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Recognition Request 1:
                Check SWIrcnd token RSTT=stop and SWIstop token MODE=TIMEOUT
                Check SWIrslt and NUANwvfm events don't appear in the call logs
            b) Recognition Request 2: 
                Check successful recognition SWIrslt token CNTNT contains expected result
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        # recognize 1 :init
        test_audio1 = 'silence1s_01234.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_noInputTimeout1 = 500
        test_expect11 = "code: 404"
        test_expect12 = 'message: \"No Speech\"'
        test_recogParams1 = client.recognition_parameters(noInputTimeout=test_noInputTimeout1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)

        # recognize 2: init
        test_audio2 = 'silence1s_01234.ulaw'
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        test_noInputTimeout2 = 1200
        test_expect2 = '<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>01234<\/instance.+\/interpretation.+\/result>'
        test_recogParams2 = client.recognition_parameters(noInputTimeout=test_noInputTimeout2)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams2, recogRes=test_recogRes2)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect11, status_code=404, status_message="No-Input Timeout (audio silence)")
        test_record_1.set_checklist_types(["Recognition", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="stop")
        test_record_1.add_token_to_checklist(evnt="SWIstop", token="MODE", value="TIMEOUT")
        test_record_1.add_undesired_to_checklist("SWIrslt")
        test_record_1.add_undesired_to_checklist("NUANwvfm")

        test_record_2 = kafka.create_messages_record(recogInit=test_recInit2, expected_result=test_expect2)
        test_record_2.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_2.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect2)

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
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            #
            kafka.validate_callLogs([test_record_1, test_record_2])
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test024_Recognition_complete_timeout_invalid(self):
        """
        Test NRC recognition parameter complete_timeout_ms set to -1  (invalid value) - recognize '945015260.ulaw'
        Expect NRC recognize return code 400 (bad requests) for invalid settings
        """
        client = gRPCClient()
        # recognize 1 :init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_completeTimeout1 = -1
        test_expect11 = "code: 400"
        test_expect12 = 'message: \"Bad Request\"'
        test_expect13 = 'details: \"The complete_timeout_ms parameter is out of range. .+\"'
        test_recogParams1 = client.recognition_parameters(completeTimeout=test_completeTimeout1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect13)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test025_Recognition_complete_timeout_disabled(self):
        """
        Test NRC recognition parameter complete_timeout_ms set to 0 (disabled) - recognize '945015260.ulaw' &  'yes.ulaw'
        Expect NRC recognize success for both cases
        """
        client = gRPCClient()
        # recognize 1 :init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_completeTimeout1 = 0
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"
        test_recogParams1 = client.recognition_parameters(completeTimeout=test_completeTimeout1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)

        # recognize 2: init
        test_audio2 = 'yes.ulaw'
        test_grammar_type2 = 'inline_grammar'
        test_grammar_data2 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type2 = 'srgsxml'
        test_completeTimeout2 = 0
        test_expect2 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        test_recogParams2 = client.recognition_parameters(completeTimeout=test_completeTimeout2)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2, mediaType=test_media_type2)
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
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test026_Recognition_complete_timeout_ok(self):
        """
        Test NRC recognition parameter complete_timeout_ms set to a very low value (10ms) then reasonable value (2000ms) - recognize separately with same audio '945015260.ulaw'
        Expect 
        1) [Test Case] NRC recognize return only 1 digit recognized for 1st case and return all the 9 digits recognized for 2nd case
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Recognition Request 1:
                Check SWIrcnd has token ENDR=ctimeout (reason for end of speech=complete_timeout)
                Check successful recognition SWIrslt token CNTNT contains expected result
            b) Recognition Request 2: 
                Check SWIrcnd has token ENDR=eeos (reason for end of speech=external_end_of_speech != complete_timeout)
                Check successful recognition SWIrslt token CNTNT contains expected result
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        # recognize 1 :init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_completeTimeout1 = 10
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>9<\/instance.+\/interpretation.+\/result>"
        test_recogParams1 = client.recognition_parameters(completeTimeout=test_completeTimeout1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)

        # recognize 2: init
        test_audio2 = '945015260.ulaw'
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        test_completeTimeout2 = 2000
        test_expect2 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"
        test_recogParams2 = client.recognition_parameters(completeTimeout=test_completeTimeout2)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams2, recogRes=test_recogRes2)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="ENDR", value="ctimeout")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect1)

        test_record_2 = kafka.create_messages_record(recogInit=test_recInit2, expected_result=test_expect2)
        test_record_2.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_2.add_token_to_checklist(evnt="SWIrcnd", token="ENDR", value="eeos")
        test_record_2.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect2)
        
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
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            #
            kafka.validate_callLogs([test_record_1, test_record_2])
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test027_Recognition_incomplete_timeout_invalid(self):
        """
        Test NRC recognition parameter incomplete_timeout_ms set to -1 (invalid value) - recognize '945015260.ulaw'
        Expect NRC recognize return code 400 (bad requests) for invalid settings
        """
        client = gRPCClient()
        # recognize 1 :init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_incompleteTimeout1 = -1
        test_expect11 = "code: 400"
        test_expect12 = 'message: \"Bad Request\"'
        test_expect13 = 'details: \"The incomplete_timeout_ms parameter is out of range.+\"'
        test_recogParams1 = client.recognition_parameters(incompleteTimeout=test_incompleteTimeout1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect13)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test028_Recognition_incomplete_timeout_disabled(self):
        """
        Test NRC recognition parameter incomplete_timeout_ms set to 0 (disabled, zero-length silence period) - recognize '945015260.ulaw' &  'yes.ulaw'
        Expect NRC recognize success for both cases
        """
        client = gRPCClient()

        # recognize 1 :init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_incompleteTimeout1 = 0
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945<\/instance.+\/interpretation.+\/result>"
        test_recogParams1 = client.recognition_parameters(incompleteTimeout=test_incompleteTimeout1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test029_Recognition_incomplete_timeout_ok(self):
        """
        Test NRC recognition parameter incomplete_timeout_ms set to a very low value (10ms) then set a default value (1500ms) - recognize separately with same audio '945015260.ulaw'
        Expect 
        1) [Test Case] NRC recognize return only partial - 3 digits recognized for 1st case and return all of the 9 digits recognized for 2nd case
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Recognition Request 1:
                Check SWIrcnd has token ENDR=itimeout (reason for end of speech = incomplete_timeout)
                Check successful recognition SWIrslt token CNTNT contains expected result
            b) Recognition Request 2: 
                Check SWIrcnd has token ENDR=eeos (reason for end of speech = external_end_of_speech != incomplete_timeout)
                Check successful recognition SWIrslt token CNTNT contains expected result
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        # recognize 1 :init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_incompleteTimeout1 = 10
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945<\/instance.+\/interpretation.+\/result>"
        test_recogParams1 = client.recognition_parameters(incompleteTimeout=test_incompleteTimeout1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)

        # recognize 2: init
        test_audio2 = '945015260.ulaw'
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        test_incompleteTimeout2 = 1500
        test_expect2 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"
        test_recogParams2 = client.recognition_parameters(incompleteTimeout=test_incompleteTimeout2)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams2, recogRes=test_recogRes2)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="ENDR", value="itimeout")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect1)

        test_record_2 = kafka.create_messages_record(recogInit=test_recInit2, expected_result=test_expect2)
        test_record_2.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_2.add_token_to_checklist(evnt="SWIrcnd", token="ENDR", value="eeos")
        test_record_2.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect2)

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
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            #
            kafka.validate_callLogs([test_record_1, test_record_2])

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test030_Recognition_max_speech_timeout_invalid(self):
        """
        Test NRC recognition parameter max_speech_timeout_ms set to 0 & -2  (not allowed, invalid value) - recognize '945015260.ulaw' &  'yes.ulaw'
        Expect NRC recognize return code 400 (bad requests) for both invalid settings
        """
        client = gRPCClient()
        # recognize 1 :init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_maxSpeechTimeout1 = -2
        test_expect11 = "code: 400"
        test_expect12 = 'message: \"Bad Request\"'
        test_expect13 = 'details: \"The max_speech_timeout_ms parameter is out of range.+\"'
        test_recogParams1 = client.recognition_parameters(maxSpeechTimeout=test_maxSpeechTimeout1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect13)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test031_Recognition_max_speech_timeout_disabled(self):
        """
        Test NRC recognition parameter max_speech_timeout_ms set to 0 or -1 (disabled) - recognize '945015260.ulaw' &  'yes.ulaw'
        Expect 
        1) [Test Case] NRC recognize success for both cases
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) For both recognitions:
                Check SWIrcnd has token ENDR=eeos
                Check successful recognition SWIrslt token CNTNT contains expected result
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        # recognize 1:
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_maxSpeechTimeout1 = 0
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"
        test_recogParams1 = client.recognition_parameters(maxSpeechTimeout=test_maxSpeechTimeout1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)

        # recognize 2:
        test_audio2 = 'yes.ulaw'
        test_grammar_type2 = 'inline_grammar'
        test_grammar_data2 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type2 = 'srgsxml'
        test_maxSpeechTimeout2 = -1
        test_expect2 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        test_recogParams2 = client.recognition_parameters(maxSpeechTimeout=test_maxSpeechTimeout2)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2, mediaType=test_media_type2)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams2, recogRes=test_recogRes2)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect1)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        test_record_2 = kafka.create_messages_record(recogInit=test_recInit2, expected_result=test_expect2)
        test_record_2.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_2.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=en-US")
        test_record_2.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect2)
        test_record_2.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"[0-9].+")

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
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            #
            kafka.validate_callLogs([test_record_1, test_record_2])
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test032_Recognition_max_speech_timeout_ok(self):
        """
        Test NRC recognition parameter max_speech_timeout_ms set to low value (100ms) and default high value (22000ms) - recognize separately with the same audio input '945015260.ulaw'
        Expect 
        1) [Test Case] NRC recognize return only partial digits result for 1st case and recognize return full 9 digit result success for 2nd case
        """
        client = gRPCClient()
        # recognize 1 :init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_maxSpeechTimeout1 = 100
        #test_expect1 = "SWIrec_STATUS_MAX_SPEECH"
        test_expect1 = "MAX_SPEECH"
        #test_expect1 =  ""
        test_recogParams1 = client.recognition_parameters(maxSpeechTimeout=test_maxSpeechTimeout1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)

        # recognize 2: init
        test_audio2 = '945015260.ulaw'
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        test_maxSpeechTimeout2 = 22000
        test_expect2 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"
        test_recogParams2 = client.recognition_parameters(maxSpeechTimeout=test_maxSpeechTimeout2)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams2, recogRes=test_recogRes2)

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
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test033_Recognition_speech_detector_sensitivity_ok(self):
        """
        Test NRC recognition parameter speech_detection_sensitivity set to valid low value (0.0) and high value (1.0) - recognize separately on the same audio high volume with noise '945015260_high2.ulaw'
        Expect 
        1) [Test Case] NRC recognize return successful for the 1st recognition sensitivity with low setting (0.0) and failed as no match for the 2nd test with high setting (1.0)
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Recognition Request 1:
                Check SWIrcnd has token ENDR=eeos
                Check successful recognition SWIrslt token CNTNT contains expected result
            b) Recognition Request 2: 
                
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        # recognition 1: init
        test_audio1 = '945015260_high2.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_speechDetectionSensitivity1 = 0.0
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"
        test_recogParams1 = client.recognition_parameters(speechDetectionSensitivity=test_speechDetectionSensitivity1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)

        # recognize 2: init
        test_audio2 = '945015260_high2.ulaw'
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        test_speechDetectionSensitivity1 = 1.0
        test_expect2 = "NO_MATCH"
        test_expect2 = ""
        test_recogParams2 = client.recognition_parameters(speechDetectionSensitivity=test_speechDetectionSensitivity1)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams2, recogRes=test_recogRes2)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="ENDR", value="eeos")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect1)

        test_record_2 = kafka.create_messages_record(recogInit=test_recInit2, expected_result=test_expect2, result_status="NO_MATCH")
        test_record_2.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_2.add_undesired_to_checklist("SWIrslt")

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(3)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(3)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            self.debug(msg)
            print(msg)  # for debug
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

    def test034_Recognition_speech_detector_sensitivity_invalid(self):
        """
        Test NRC recognition parameter speech_detection_sensitivity set to invalid negative value -0.1 and high value 1.1 (over limit 0.0 to 1.0) - recognize separately with the same audio '945015260.ulaw'
        Expect NRC recognize return fails for both 1st test with invalid value -0.1 < 0 and 2nd test with invalid value 1.1.> 1.0
        """
        client = gRPCClient()
        # recognition 1: init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_speechDetectionSensitivity1 = -0.1
        test_expect11 = "code: 400"
        test_expect12 = ".+Bad Request"
        test_expect13 = ".+The speech_detection_sensitivity parameter is out of range.+"
        test_recogParams1 = client.recognition_parameters(speechDetectionSensitivity=test_speechDetectionSensitivity1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)

        # recognize 2: init
        test_audio2 = '945015260.ulaw'
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        test_speechDetectionSensitivity1 = 1.1
        test_expect21 = "code: 400"
        test_expect22 = ".+Bad Request"
        test_expect23 = ".+The speech_detection_sensitivity parameter is out of range.+"
        test_recogParams2 = client.recognition_parameters(speechDetectionSensitivity=test_speechDetectionSensitivity1)
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
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect13)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect21)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect22)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect23)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test035_Recognition_recognizer_parameters1(self):
        """
        Test NRC recognition recognizer_parameters set swirec_suppress_waveform_logging to 'false' and swirec_suppress_event_logging to 'false' with audio '945015260.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Manual validation] verify utterance from this case via QA NRC scripts (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) waveform logging (file) found and playable (user input utterance), such as: NUAN-xx-xx-nrc-xxxxxxx-krwcs-xxxxxxxxx-utt01-PLAYABLE.wav
        3) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) recognizer related events all presented in the call log, including: SWIrcst, SWIrcnd, SWIrslt (part of Recognition type)
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        # recognition 1: init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_recognizerParameters1 = {"swirec_suppress_waveform_logging": "false", "swirec_suppress_event_logging": "false"}
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"
        
        test_recogParams1 = client.recognition_parameters(recognizerParameters=test_recognizerParameters1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1, status_code=400)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect1)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")
        
        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test036_Recognition_recognizer_parameters2(self):
        """
        Test NRC recognition recognizer_parameters set swirec_suppress_waveform_logging to 'true' and swirec_suppress_event_logging to 'true' with audio '945015260.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Manual validation] verify utterance from this case via QA NRC scripts (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Cannot find waveform logging(user input utterance recorded file), such as: NUAN-xx-xx-nrc-xxxxxxx-krwcs-xxxxxxxxx-utt01-PLAYABLE.wav
        3) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Cannot find recognizer related events from this case call log, including: SWIrcst, SWIrcnd, SWIrslt;
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        # recognition 1: init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_recognizerParameters1 = {"swirec_suppress_waveform_logging": "true", "swirec_suppress_event_logging": "true"}
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"
        
        test_recogParams1 = client.recognition_parameters(recognizerParameters=test_recognizerParameters1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_undesired_to_checklist("SWIrcst")
        test_record_1.add_undesired_to_checklist("SWIrcnd")
        test_record_1.add_undesired_to_checklist("SWIrslt")
        test_record_1.add_undesired_to_checklist("NUANwvfm")
        
        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()
            kafka.cleanup()

    def test037_Recognition_recognizer_parameters_invalid(self):
        """
        Test NRC recognition recognizer_parameters by invalid parameter & value with audio '945015260.ulaw'
        Expect: NRC recognize return failed with error code 400 and mesage 'Bad request'
        """
        client = gRPCClient()
        # recognition 1: init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_recognizerParameters1 = {"invalidxxxxx": "invaidxxxx"}
        test_expect11 = "code: 400"
        test_expect12 = "message: \"Bad Request\""
        test_expect13 = "details: \"Failed to set parameter: invalidxxxxx=invaidxxxx - Reason: invalid parameter\""
        test_recogParams1 = client.recognition_parameters(recognizerParameters=test_recognizerParameters1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)

        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect13)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test038_Recognition_endpointer_parameters1(self):
        """
        Test NRC recognition endpointer_parameters set swiep_suppress_waveform_logging to 'false' and swiep_suppress_event_logging to 'false' with audio '945015260.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Manual validation] verify utterance from this case via QA NRC scripts (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Found endpointer waveform logging file (prior to endpointing): PREWVNM.wav file and WVNM.txt file (endpointer parameters file)
        3) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Found endpointer related events presented from this case call log, including: SWIepst, SWIepms (part of Endpointer type)
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        # recognition 1: init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_endpointerParameters1 = {"swiep_suppress_waveform_logging": "false", "swiep_suppress_event_logging": "false"}
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"
        test_recogParams1 = client.recognition_parameters(endpointerParameters=test_endpointerParameters1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect1)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")
        
        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            #
            kafka.validate_callLogs(test_record_1)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test039_Recognition_endpointer_parameters2(self):
        """
        Test NRC recognition endpointer_parameters set swiep_suppress_waveform_logging to 'true' and swiep_suppress_event_logging to 'true' with audio '945015260.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Manual validation] verify utterance from this case via QA NRC scripts (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Cannot find endpointer waveform logging file (prior to endpointing): PREWVNM.wav file and WVNM.txt file (endpointer parameters file)
        3) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Cannot find endpointer related events presented from this case call log, including: SWIepst, SWIepms
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        # recognition 1: init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_endpointerParameters1 = {"swiep_suppress_waveform_logging": "true", "swiep_suppress_event_logging": "true"}
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"
        test_recogParams1 = client.recognition_parameters(endpointerParameters=test_endpointerParameters1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect1)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")
        test_record_1.add_undesired_to_checklist("SWIepst")
        test_record_1.add_undesired_to_checklist("SWIepms")

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test040_Recognition_endpointer_parameters_invalid(self):
        """
        Test NRC recognition endpointer_parameters by invalid parameter & value with audio '945015260.ulaw'
        Expect: NRC recognize return failed with error code 400 and mesage 'Bad request'
        """
        client = gRPCClient()
        # recognition 1: init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_endpointerParameters1 = {"invalidxxxxx": "invaidxxxx"}
        test_expect11 = "code: 400"
        test_expect12 = "message: \"Bad Request\""
        test_expect13 = "details: \"Failed to set parameter: invalidxxxxx=invaidxxxx - Reason: invalid parameter\""
        test_recogParams1 = client.recognition_parameters(endpointerParameters=test_endpointerParameters1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)

        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect13)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test041_Recognition_set_cookie_ok(self):
        """
        Test NRC recognition cookies with uri-grammar ("uri_grammar_yes.grxml") when set cookies "Set-Cookie:name=cookie1;value=value1","Set-Cookie2:name=cookie2;value=value2"
        Expect:
        1) [Test case] NRC recognize with cookie & uri-grammar return successful
        2) [Manual validation] verify cookies via tcpdump on QA Apache server which uri-grammar fetched from this case (see testServerConfig.yaml defined: NRCTestResURL: use client.test_res_url)
            a) Start tcpdump on QA Apache server: tcpdump -w nrc_cookies1.pcap -i any port 80
            b) run this NRC cookie test case
            c) stop tcpdump and view captured http traffic file (.pcap) via Wireshark
            d) Verify if tcpdump log contain cookies when fetch uri-grammar from this case - new customized cookies should be found from http GET method for uri-grammar file
        """
        client = gRPCClient()
        #
        test_audio = 'yes.ulaw'
        test_grammar = "uri_grammar_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        # test_cookies = ["Set-Cookie:name=cookie1;value=value1", "Set-Cookie2:name=cookie2;value=value2"] # old
        test_cookies = ["Set-Cookie:name=cookie1;value=value1;path=/", "Set-Cookie2:name=cookie2;value=value2;path=/"]
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters(cookieSet=test_cookies)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test042_Recognition_set_cookie_empty(self):
        """
        Test NRC recognition cookies with uri-grammar ("uri_grammar_yes.grxml") when set cookies empty "Set-Cookie:name=cookie1;value=''","Set-Cookie2:name=cookie2;value=''"
        Expect:
        1) [Test case] NRC recognize with cookie & uri-grammar return successful.
        2) [Manual validation] verify cookies via tcpdump on QA Apache server which uri-grammar fetched from this case (see testServerConfig.yaml defined: NRCTestResURL: use client.test_res_url)
            a) Start tcpdump on QA Apache server: tcpdump -w nrc_cookies1.pcap -i any port 80
            b) run this NRC cookie test case
            c) stop tcpdump and view captured http traffic file (.pcap) via Wireshark
            d) Verify if tcpdump log contain cookies when fetch uri-grammar from this case - no cookies found since empty value delete the cookie
        """
        client = gRPCClient()
        #
        test_audio = 'yes.ulaw'
        test_grammar = "uri_grammar_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        # test_cookies = ["Set-Cookie:name=cookie1;value=''", "Set-Cookie2:name=cookie2;value=''"] # old
        test_cookies = ["Set-Cookie:name=cookie1;value='';path=/", "Set-Cookie2:name=cookie2;value='';path=/"]
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters(cookieSet=test_cookies)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test043_Recognition_set_cookie_invalid(self):
        """
        Test NRC recognition cookies with uri-grammar ("uri_grammar_yes.grxml") when set cookies empty "Set-Cookie:name=cookie1;value=''","Set-Cookie2:name=cookie2;value=''"
        Expect:
        1) [Test case] NRC recognize with cookie & uri-grammar return successful.
        2) [Manual validation] verify cookies via tcpdump on QA Apache server which uri-grammar fetched from this case (see testServerConfig.yaml defined: NRCTestResURL, use client.test_res_url)
            a) Start tcpdump on QA Apache server: tcpdump -w nrc_cookies1.pcap -i any port 80
            b) run this NRC cookie test case
            c) stop tcpdump and view captured http traffic file (.pcap) via Wireshark
            d) Verify if tcpdump log contain cookies when fetch uri-grammar from this case - no cookies found since empty value delete the cookie
        """
        client = gRPCClient()
        #
        test_audio = 'yes.ulaw'
        test_grammar = "uri_grammar_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        test_cookies = ["xxxx", "xxxx"]
        test_expect11 = "code: 400"
        test_expect12 = "message: \"Bad Request\""
        test_expect13 = "details: \"Invalid cookie format.+"

        test_recogParams = client.recognition_parameters(cookieSet=test_cookies)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect13)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test044_Recognition_secure_context_level_open(self):
        """
        Test NRC recognition secure_context_level parameter when set to OPEN with audio '945015260.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Manual validation] verify NRC utterance from this case via QA NRC scripts (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the diagnostic logs
            b) utterance waveforms are recorded & playable (user input utterance), such as: NUAN-xx-xx-nrc-xxxxxxx-krwcs-xxxxxxxxx-utt01-PLAYABLE.wav
        3) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs: 
                Event "SWIrcnd" should have tokens RSTT=ok, RENR=ok, ENDR=eeos, NBST=2, MPNM=en.us/10.0.2/models/FirstPass/models.hmm, 
                Event "SWIrslt" should have tokens MEDIA=application/x-vnd.speechworks.emma+xml
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        # recognition 1: init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        
        test_secureContextLevel = 'OPEN'
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"
        test_recogParams1 = client.recognition_parameters(secureContextLevel=test_secureContextLevel)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect1)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="ok")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RENR", value="ok")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="ENDR", value="eeos")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="NBST", value="2")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="MPNM", value="en.us/10.0.2/models/FirstPass/models.hmm")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="MEDIA", value="application/x-vnd.speechworks.emma+xml")

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()
            kafka.cleanup()

    def test045_Recognition_secure_context_level_suppress(self):
        """
        Test NRC recognition secure_context_level parameter when set to SUPPRESS with audio '945015260.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Manual validation] verify NRC utterance from this case via QA NRC scripts (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results SUPPRESSED in the diagnostic logs.
            b) No utterance waveforms are recorded & playable from this test (user input utterance), such as: NUAN-xx-xx-nrc-xxxxxxx-krwcs-xxxxxxxxx-utt01-PLAYABLE.wav
        3) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results SUPPRESSED in the call logs.
                Event "SWIrcnd" should have tokens SECURE=TRUE, RSTT=ok, RENR=ok, ENDR=eeos, NBST=2, RSLT=_SUPPRESSED, RAWT=_SUPPRESSED, SPOK=_SUPPRESSED, KEYS=_SUPPRESSED, WVNM=_SUPPRESSED, MPNM=en.us/10.0.2/models/FirstPass/models.hmm
                Event "SWIrslt" should have tokens SECURE=TRUE, MEDIA=application/x-vnd.speechworks.emma+xml, CNTNT=_SUPPRESSED 
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        # recognition 1: init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_secureContextLevel = 'SUPPRESS'
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"
        test_recogParams1 = client.recognition_parameters(secureContextLevel=test_secureContextLevel)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1, secure_clog=True)
        test_record_1.set_checklist_types(["Recognition", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="ok")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RENR", value="ok")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="ENDR", value="eeos")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="NBST", value="2")
        test_record_1.add_token_to_checklist(evnt="NUANwvfm", token="PLAYABLE", value="_SUPPRESSED")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RSLT", value="_SUPPRESSED")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RAWT", value="_SUPPRESSED")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="SPOK", value="_SUPPRESSED")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="KEYS", value="_SUPPRESSED")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="WVNM", value="_SUPPRESSED")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="MPNM", value="en.us/10.0.2/models/FirstPass/models.hmm")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="SECURE", value="TRUE")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="MEDIA", value="application/x-vnd.speechworks.emma+xml")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="_SUPPRESSED")

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            #
            kafka.validate_callLogs(test_record_1)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test300_Recognition_nBest_Invalid_Negative(self):
        """
        Test NRC recognition with nBest set to -1
        Expect NRC Bad Request - he nbest parameter is out of range. Valid range is [0, 999]
        """
        client = gRPCClient()
        #
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_nBest1 = -1
        test_confLevel = 0  # set it to 0, which always sets the result status to success providing that Recognizer was able to populate the n-best list.

        test_expect11 = "code: 400"
        test_expect12 = "message: \"Bad Request\""
        test_expect13 = "details: \"The nbest parameter is out of range. Valid range is \[0, 999\].\""

        test_recogParams1 = client.recognition_parameters(confLevel=test_confLevel, nBest=test_nBest1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect13)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test301_Recognition_nBest_Invalid_Exceed_Max(self):
        """
        Test NRC recognition with nBest set to 1000
        Expect NRC Bad Request - he nbest parameter is out of range. Valid range is [0, 999]
        """
        client = gRPCClient()
        #
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_nBest1 = -1
        test_confLevel = 0  # set it to 0, which always sets the result status to success providing that Recognizer was able to populate the n-best list.

        test_expect11 = "code: 400"
        test_expect12 = "message: \"Bad Request\""
        test_expect13 = "details: \"The nbest parameter is out of range. Valid range is \[0, 999\].\""

        test_recogParams1 = client.recognition_parameters(confLevel=test_confLevel, nBest=test_nBest1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect13)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test302_Recognition_speech_detector_sensitivity_Exceed_Max(self):
        """
        Test NRC recognition parameter speech_detection_sensitivity set to invalid negative value -0.1 and high value 1.1 (over limit 0.0 to 1.0) - recognize separately with the same audio '945015260.ulaw'
        Expect NRC recognize return fails for both 1st test with invalid value -0.1 < 0 and 2nd test with invalid value 1.1.> 1.0
        """
        client = gRPCClient()
        # recognition 1: init
        test_audio1 = '945015260.ulaw'
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_speechDetectionSensitivity1 = 2.0
        test_expect11 = "code: 400"
        test_expect12 = ".+Bad Request"
        test_expect13 = ".+The speech_detection_sensitivity parameter is out of range.+"
        test_recogParams1 = client.recognition_parameters(speechDetectionSensitivity=test_speechDetectionSensitivity1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)

        # recognize 2: init
        test_audio2 = '945015260.ulaw'
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        test_speechDetectionSensitivity1 = 1.1
        test_expect21 = "code: 400"
        test_expect22 = ".+Bad Request"
        test_expect23 = ".+The speech_detection_sensitivity parameter is out of range.+"
        test_recogParams2 = client.recognition_parameters(speechDetectionSensitivity=test_speechDetectionSensitivity1)
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
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect13)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect21)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect22)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect23)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            
    def test310_Recognition_StallTimers_True_10s_silence_01234(self):
        """
        Test NRC recognition flag - stall_timers = True. (default = false)
        No Input Time default is 7s.
        Audio input is 10seconds of silence followed by 01234.
        Expected Result: Due to stall_timers = True, Recognizer will wait for input. Successful Recognition.
        """
        client = gRPCClient()
        test_audio = "silence10s_01234.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_stall_timers = True
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+instance.+01234.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(recognizerFlags=test_stall_timers)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)

            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test311_Recognition_StallTimers_False(self):
        """
        Test NRC recognition flag - stall_timers = False. (default = false)
        No Input Time default is 7s.
        Audio input is 10seconds of silence followed by 01234.
        Expected Result: Due to stall_timers = False, call ends due to No Input Timeout tiggered at 7 seconds
        """
        client = gRPCClient()
        test_audio = "silence10s_01234.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_stall_timers = False
        test_expect11 = "code: 404"
        test_expect12 = 'message: \"No Speech\"'

        test_recogParams = client.recognition_parameters(recognizerFlags=test_stall_timers)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect12)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test312_Recognition_StallTimers_True(self):
        """
        Test NRC recognition flag - stall_timers = True. (default = false)
        No Input Time default is 7s.
        Audio input is 01234.
        Expected Result: Due to stall_timers = True, Recognizer will wait for input. Successful Recognition.
        """
        client = gRPCClient()
        test_audio = "01234.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_stall_timers = True
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+instance.+01234.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(recognizerFlags=test_stall_timers)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test313_Recognition_StallTimers_Invalid(self):
        """
        This is a test harness negative test.
        Test NRC recognition flag - stall_timers = ABC (invalid). (default = false)
        No Input Time default is 7s.
        Audio input is 1 01234.
        Expected Result: Test harness will default to false.
        """
        client = gRPCClient()
        test_audio = "01234.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_stall_timers = 'ABC'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+instance.+01234.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(recognizerFlags=test_stall_timers)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)

            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test314_Recognition_StallTimers_True_Numeric(self):
        """
        Test NRC recognition flag - stall_timers = 1. (default = false)
        No Input Time default is 7s.
        Audio input is 10s silence 01234.
        Expected Result: Due to stall_timers = True (1), Recognizer will wait for input. Successful Recognition.
        """
        client = gRPCClient()
        test_audio = "silence10s_01234.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_stall_timers = 1
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+instance.+01234.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(recognizerFlags=test_stall_timers)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test315_Recognition_StallTimers_False_Numeric(self):
        """
        Test NRC recognition flag - stall_timers = 0. (default = false)
        No Input Time default is 7s.
        Audio input is 10s silence 01234.
        Expected Result: Due to stall_timers = False (0), Recognizer will not wait for input. S.
        """
        client = gRPCClient()
        test_audio = "silence10s_01234.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_stall_timers = 0
        test_expect11 = "code: 404"
        test_expect12 = 'message: \"No Speech\"'

        test_recogParams = client.recognition_parameters(recognizerFlags=test_stall_timers)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect12)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            
    def test316_Recognition_StallTimers_Invalid_Numeric(self):
        """
        This is a test harness negative test.
        Test NRC recognition flag - stall_timers = 3 (invalid). (default = false)
        No Input Time default is 7s.
        Audio input is 01234.
        Expected Result: Test harness will default to false.
        """
        client = gRPCClient()
        test_audio = "01234.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_stall_timers = 3
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+instance.+01234.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(recognizerFlags=test_stall_timers)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)

            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            
    def test317_Recognition_StallTimers_True_Control_0ms(self):
        """
        Test NRC recognition flag - stall_timers = True. (default = false)
        Control Message time = 0s
        No Input Time default is 7s.
        Audio input is 10seconds of silence followed by 01234.
        Expected Result: Due to stall_timers = True, No Input Timeout will only start counting once it receives
            the Control message. In this case, at 0s. Due to the 10s of silence, a timeout occurs.
        """
        client = gRPCClient()
        test_audio = "silence10s_01234.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_stall_timers = True
        test_control_time = 0
        test_expect11 = "code: 404"
        test_expect12 = 'message: \"No Speech\"'

        test_recogParams = client.recognition_parameters(recognizerFlags=test_stall_timers)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_Control = client.recognition_control(rec_control_time=test_control_time)
        #
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)

            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect12)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test318_Recognition_StallTimers_True_Control_2900ms(self):
        """
        Test NRC recognition flag - stall_timers = True. (default = false)
        Control Message time = 2900ms
        No Input Time default is 7s.
        Audio input is 10seconds of silence followed by 01234.
        Expected Result: Due to stall_timers = True, No Input Timeout will only start counting once it receives
            the Control message. In this case, at 2.9s. Due to the 10s of silence, a timeout occurs at 9.9 seconds.
        """
        client = gRPCClient()
        test_audio = "silence10s_01234.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_stall_timers = True
        test_control_time = 2900
        test_expect11 = "code: 404"
        test_expect12 = 'message: \"No Speech\"'

        test_recogParams = client.recognition_parameters(recognizerFlags=test_stall_timers)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_Control = client.recognition_control(rec_control_time=test_control_time)
        #
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)

            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect12)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test319_Recognition_StallTimers_True_Control_3100ms(self):
        """
        Test NRC recognition flag - stall_timers = True. (default = false)
        Control Message time = 3100ms
        No Input Time default is 7s.
        Audio input is 10seconds of silence followed by 01234.
        Expected Result: Due to stall_timers = True, No Input Timeout will only start counting once it receives
            the Control message. In this case, at 3.1s. Due to the 10s of silence, an recognition begins 10.1 seconds.
        """
        client = gRPCClient()
        test_audio = "silence10s_01234.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_stall_timers = True
        test_control_time = 3100
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+instance.+01234.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(recognizerFlags=test_stall_timers)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_Control = client.recognition_control(rec_control_time=test_control_time)
        #
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)

            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test320_Recognition_StallTimers_True_NoInputTimeout_3000ms_Control_6900ms(self):
        """
        Test NRC recognition flag - stall_timers = True. (default = false)
        Control Message time = 6900ms
        No Input Time 3000s.
        Audio input is 10 seconds of silence followed by 01234.
        Expected Result: Due to stall_timers = True, No Input Timeout is set to 3s, will only start counting once it receives
            the Control message. In this case, at 6.9s. Due to the 10s of silence, a timeout occurs at 9.9 seconds.
        """
        client = gRPCClient()
        # recognize 1 :init
        test_audio1 = "silence10s_01234.ulaw"
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_stall_timers = True 
        test_control_time = 6900        
        test_noInputTimeout1 = 3000
        test_expect11 = "code: 404"
        test_expect12 = 'message: \"No Speech\"'
        test_recogParams1 = client.recognition_parameters(noInputTimeout=test_noInputTimeout1, recognizerFlags=test_stall_timers)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        test_Control = client.recognition_control(rec_control_time=test_control_time)
        #
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)

            #
            msg = "Test recognition result 1: \n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect12)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test321_Recognition_StallTimers_True_NoInputTimeout_3000ms_Control_7100ms(self):
        """
        Test NRC recognition flag - stall_timers = True. (default = false)
        Control Message time = 6900ms
        No Input Time 3000s.
        Audio input is 10 seconds of silence followed by 01234.
        Expected Result: Due to stall_timers = True, No Input Timeout is set to 3s, will only start counting once it receives
            the Control message. In this case, at 7.1s. Due to the 10s of silence, an recognition begins 10.1 seconds.
        """
        client = gRPCClient()
        # recognize 1 :init
        test_audio1 = "silence10s_01234.ulaw"
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_stall_timers = True 
        test_control_time = 7100        
        test_noInputTimeout1 = 3000
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+instance.+01234.+\/interpretation.+\/result>"
        test_recogParams1 = client.recognition_parameters(noInputTimeout=test_noInputTimeout1, recognizerFlags=test_stall_timers)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        test_Control = client.recognition_control(rec_control_time=test_control_time)
        #
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)

            #
            msg = "Test recognition result 1: \n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test322_Recognition_StallTimers_False_Control_0s(self):
        """
        Test NRC recognition flag - stall_timers = False. (default = false)
        Control Message time = 0s
        No Input Time default is 7s.
        Audio input is 10seconds of silence followed by 01234.
        Expected Result: Due to stall_timers = False, No Input Timeout will only start counting once it receives
            the Control message. In this case, at 0s. Due to the 10s of silence, a timeout occurs.
        """
        client = gRPCClient()
        test_audio = "silence10s_01234.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_stall_timers = False
        test_control_time = 0
        test_expect11 = "code: 404"
        test_expect12 = 'message: \"No Speech\"'

        test_recogParams = client.recognition_parameters(recognizerFlags=test_stall_timers)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_Control = client.recognition_control(rec_control_time=test_control_time)
        #
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)

            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect12)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test323_Recognition_StallTimers_False_Control_3100ms(self):
        """
        Test NRC recognition flag - stall_timers = False. (default = false)
        Control Message time = 3100ms
        No Input Time default is 7s.
        Audio input is 10seconds of silence followed by 01234.
        Expected Result: Due to stall_timers = False, No Input Timeout will only start counting once it receives
            the Control message. In this case, at 3.1s. Due to the 10s of silence, and stall_timers=false, an No Input Timeout is encountered.
        """
        client = gRPCClient()
        test_audio = "silence10s_01234.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_stall_timers = False
        test_control_time = 3100
        test_expect11 = "code: 404"
        test_expect12 = 'message: \"No Speech\"'

        test_recogParams = client.recognition_parameters(recognizerFlags=test_stall_timers)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_Control = client.recognition_control(rec_control_time=test_control_time)
        #
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)

            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect12)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test324_Recognition_StallTimers_False_NoInputTimeout_3000ms_Control_7100ms(self):
        """
        Test NRC recognition flag - stall_timers = False. (default = false)
        Control Message time = 6900ms
        No Input Time 3000s.
        Audio input is 10 seconds of silence followed by 01234.
        Expected Result: Due to stall_timers = False, No Input Timeout is set to 3s, will only start counting once it receives
            the Control message. In this case, at 7.1s. Due to the 10s of silence, and stall_timers=false, an No Input Timeout is encountered.
        """
        client = gRPCClient()
        test_audio1 = "silence10s_01234.ulaw"
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_stall_timers = False 
        test_control_time = 7100        
        test_noInputTimeout1 = 3000
        test_expect11 = "code: 404"
        test_expect12 = 'message: \"No Speech\"'
        test_recogParams1 = client.recognition_parameters(noInputTimeout=test_noInputTimeout1, recognizerFlags=test_stall_timers)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        test_Control = client.recognition_control(rec_control_time=test_control_time)
        #
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)

            #
            msg = "Test recognition result 1: \n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect12)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()


    def test500_Recognition_Confidence_Invalid_Low(self):
        """
        Test invalid parameter confidence level invalid too low.
        Expect:
            error code: 400
            message: "Bad Request"
            details: "The confidence_level parameter is out of range. Valid range is [0, 1.0]."
        """
        client = gRPCClient()

        test_audio = "yes.ulaw"
        test_audio_format = 'ulaw'
        test_confLevel = -1
        test_expect1 = 'code: 400'
        test_expect2 = 'message: "Bad Request"'
        test_expect3 = 'The confidence_level parameter is out of range.'
        
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format, confLevel=test_confLevel)
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test501_Recognition_Confidence_Invalid_High(self):
        """
        Test invalid parameter confidence level invalid too high.
        Expect:
            error code: 400
            message: "Bad Request"
            details: "The confidence_level parameter is out of range. Valid range is [0, 1.0]."
        """
        client = gRPCClient()

        test_audio = "yes.ulaw"
        test_audio_format = 'ulaw'
        test_confLevel = 12
        test_expect1 = 'code: 400'
        test_expect2 = 'message: "Bad Request"'
        test_expect3 = 'The confidence_level parameter is out of range.'
        
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format, confLevel=test_confLevel)
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
    
    def test046_NRIR_proton_feature_completetimeout_ctimeout_grammar(self):
        """
        NR IR Converted testcases:
            ./proton_feature/completetimeout/ctimeout_grammar_PERL

        Test completetimeout parameter set at 3 different levels.
        Expect:
        1) [Test case] 
            a) set completetimeout in a grammar <meta> tag. completimeout=500ms. Expect ">january the first<"
            b) set completetimeout in a grammar <meta> tag. completimeout=500ms. Expect ">january the first two_thousand five<"
            c) set completetimeout as recognition parameter (via NRC proto). completimeout=500ms. Expect ">january the first two_thousand<"
            d) set completetimeout as parameter grammar. completetimeout=250ms. Expect ">january the first<"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_jan1st_silence_600ms_2005.wav"
        test_audio_format1 = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_date_ctimeout_500ms.xml'
        test_media_type1 = 'srgsxml'
        test_completeTimeout1 = 'ignore' # special case to set completeTimeout to None in recognition request
        test_expect1 = ">january the first<"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1, completeTimeout=test_completeTimeout1)
        test_recogRes_1 = [test_recogRes1] #[test_recogRes0, test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes_1)
        #
        test_audio2 = "NRIR_jan1st_silence_300ms_2005_silence_1300ms.wav"
        test_audio_format2 = 'pcm'
        test_grammar_type2 = 'uri_grammar'
        test_grammar_data2 = 'NRIR_date_ctimeout_500ms.xml'
        test_media_type2 = 'srgsxml'
        test_completeTimeout2 = 'ignore' # special case to set completeTimeout to None in recognition request
        test_expect2 = ">january the first two_thousand five<"

        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        test_recogParams2 = client.recognition_parameters(audioFormat=test_audio_format2, completeTimeout=test_completeTimeout2)
        test_recogRes_2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams2, recogRes=test_recogRes_2)
        #
        test_audio3 = "NRIR_jan1st_silence_500ms_2000_silence_600ms_5.wav"
        test_audio_format3 = 'pcm'
        test_grammar_type3 = 'uri_grammar'
        test_grammar_data3 = 'NRIR_date_ctimeout_300ms.xml'
        test_media_type3 = 'srgsxml'
        test_completeTimeout3 = 500
        test_expect3 = ">january the first two_thousand<"

        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_uri3, mediaType=test_media_type3)
        test_recogParams3 = client.recognition_parameters(audioFormat=test_audio_format3, completeTimeout=test_completeTimeout3)
        test_recogRes_3 = [test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams3, recogRes=test_recogRes_3)
        #
        test_audio4 = "NRIR_jan1st_silence_300ms_2005_silence_1300ms.wav"
        test_audio_format4 = 'pcm'
        test_grammar_type4 = 'uri_grammar'
        test_grammar_data4 = 'NRIR_parameter_grammar_completetimeout.grxml'
        test_media_type4 = 'xswiparameter'
        test_completeTimeout4 = 'ignore' # special case to set completeTimeout to None in recognition request
        test_expect4 = ">january the first<"

        test_grammar_uri4 = client.test_res_url + test_grammar_data4
        test_recogRes4 = client.recognition_resource(grammarType=test_grammar_type4, grammarData=test_grammar_uri4, mediaType=test_media_type4)
        test_recogParams4 = client.recognition_parameters(audioFormat=test_audio_format4, completeTimeout=test_completeTimeout4)
        test_recogRes_4 = [test_recogRes1, test_recogRes4]
        test_recInit4 = client.recognition_init_repeated(recogParam=test_recogParams4, recogRes=test_recogRes_4)
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(2)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio3, recInit=test_recInit3)
            time.sleep(2)
            test_result4 = client.qa_nr_recognize_test_func1(audioInput=test_audio4, recInit=test_recInit4)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            msg += "Test recognition result 4: \n" + test_result4 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)
            self.assertRecognitionResult(inputToCheck=test_result4, expectResult=test_expect4)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test047_NRIR_osr_quantum_feature_ContraintList_Constraints_blue(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_blue_PERL
        
        Test validates recognition of colors using grammar and weighted constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "blue"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_blue2.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_colors.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_color_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect11 = "blue"
        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test048_NRIR_osr20_feature_Grammar_SWI_vars_allowable_chars_PERL(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/Grammar/SWI_vars/allowable_chars_PERL

            Test SWI_var characters setting as parameter to grammar.
            Expect:
            1) [Test Case]
                a) Audio newyork_newyork will be understood by grammar and SWI_meaning result expected to be ";"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_newyork_newyork.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_funky.xml?SWI_vars.char_val=%3B'
        test_media_type1 = 'srgsxml'
        test_expect11 = '<SWI_meaning>;</SWI_meaning>'
        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test502_NRIR_osr20_feature_Grammar_SWI_vars_allowable_chars_PERL_Slash_Symbol(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/Grammar/SWI_vars/allowable_chars_PERL

            Test SWI_var characters setting as parameter to grammar.
            Expect:
            1) [Test Case]
                a) Audio newyork_newyork will be understood by grammar and SWI_meaning result expected to be "/"
        """
        client = gRPCClient()
        #
        test_audio = "NRIR_newyork_newyork.wav"
        test_audio_format = 'pcm'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'

        # Test forward slash
        test_grammar_data1 = 'NRIR_funky.xml?SWI_vars.char_val=%2F'
        test_expect1 = '<SWI_meaning>/</SWI_meaning>'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test503_NRIR_osr20_feature_Grammar_SWI_vars_allowable_chars_PERL_Sentence_Symbols(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/Grammar/SWI_vars/allowable_chars_PERL

            Test SWI_var characters setting as parameter to grammar.
            Expect:
            1) [Test Case]
                a) Audio newyork_newyork will be understood by grammar and SWI_meaning result expected to be ":"
                b) Audio newyork_newyork will be understood by grammar and SWI_meaning result expected to be "!"
                c) Audio newyork_newyork will be understood by grammar and SWI_meaning result expected to be "."
                d) Audio newyork_newyork will be understood by grammar and SWI_meaning result expected to be ","
        """
        client = gRPCClient()
        #
        test_audio = "NRIR_newyork_newyork.wav"
        test_audio_format = 'pcm'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)

        # Test colon symbol
        test_grammar_data1 = 'NRIR_funky.xml?SWI_vars.char_val=%3A'
        test_expect1 = '<SWI_meaning>:</SWI_meaning>'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes1)
        
        # Test exclamation mark symbol
        test_grammar_data2 = 'NRIR_funky.xml?SWI_vars.char_val=!'
        test_expect2 = '<SWI_meaning>!</SWI_meaning>'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes2)

        # Test period symbol
        test_grammar_data3 = 'NRIR_funky.xml?SWI_vars.char_val=.'
        test_expect3 = '<SWI_meaning>.</SWI_meaning>'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri3, mediaType=test_media_type)
        test_recogRes3 = [test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes3)

        # Test comma symbol
        test_grammar_data4 = 'NRIR_funky.xml?SWI_vars.char_val=%2C'
        test_expect4 = '<SWI_meaning>,</SWI_meaning>'
        test_grammar_uri4 = client.test_res_url + test_grammar_data4
        test_recogRes4 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri4, mediaType=test_media_type)
        test_recogRes4 = [test_recogRes4]
        test_recInit4 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes4)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            #
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit2)
            time.sleep(1)
            #
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit3)
            time.sleep(1)
            #
            test_result4 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit4)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            msg += "Test recognition result 4: \n" + test_result4 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)
            self.assertRecognitionResult(inputToCheck=test_result4, expectResult=test_expect4)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test504_NRIR_osr20_feature_Grammar_SWI_vars_allowable_chars_PERL_Ampersand_Symbol(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/Grammar/SWI_vars/allowable_chars_PERL

            Test SWI_var characters setting as parameter to grammar.
            Expect:
            1) [Test Case]
                a) Audio newyork_newyork will be understood by grammar and SWI_meaning result expected to be "&amp;"
        """
        client = gRPCClient()
        #
        test_audio = "NRIR_newyork_newyork.wav"
        test_audio_format = 'pcm'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'

        # Test forward slash
        test_grammar_data1 = 'NRIR_funky.xml?SWI_vars.char_val=%26'
        test_expect1 = '<SWI_meaning>&amp;</SWI_meaning>'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test505_NRIR_osr20_feature_Grammar_SWI_vars_allowable_chars_PERL_Math_Symbols(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/Grammar/SWI_vars/allowable_chars_PERL

            Test SWI_var characters setting as parameter to grammar.
            Expect:
            1) [Test Case]
                a) Audio newyork_newyork will be understood by grammar and SWI_meaning result expected to be "="
                b) Audio newyork_newyork will be understood by grammar and SWI_meaning result expected to be "%"
                c) Audio newyork_newyork will be understood by grammar and SWI_meaning result expected to be "&gt;"
                d) Audio newyork_newyork will be understood by grammar and SWI_meaning result expected to be "-"
        """
        client = gRPCClient()
        #
        test_audio = "NRIR_newyork_newyork.wav"
        test_audio_format = 'pcm'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)

        # Test equality symbol
        test_grammar_data1 = 'NRIR_funky.xml?SWI_vars.char_val=%3D'
        test_expect1 = '<SWI_meaning>=</SWI_meaning>'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes1)
        
        # Test percent symbol
        test_grammar_data2 = 'NRIR_funky.xml?SWI_vars.char_val=%25'
        test_expect2 = '<SWI_meaning>%</SWI_meaning>'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes2)

        # Test greater-than symbol
        test_grammar_data3 = 'NRIR_funky.xml?SWI_vars.char_val=%3E'
        test_expect3 = '<SWI_meaning>&gt;</SWI_meaning>'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri3, mediaType=test_media_type)
        test_recogRes3 = [test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes3)

        # Test dash/minus-sign symbol
        test_grammar_data4 = 'NRIR_funky.xml?SWI_vars.char_val=-'
        test_expect4 = '<SWI_meaning>-</SWI_meaning>'
        test_grammar_uri4 = client.test_res_url + test_grammar_data4
        test_recogRes4 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri4, mediaType=test_media_type)
        test_recogRes4 = [test_recogRes4]
        test_recInit4 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes4)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            #
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit2)
            time.sleep(1)
            #
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit3)
            time.sleep(1)
            #
            test_result4 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit4)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            msg += "Test recognition result 4: \n" + test_result4 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)
            self.assertRecognitionResult(inputToCheck=test_result4, expectResult=test_expect4)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test506_NRIR_osr20_feature_Grammar_SWI_vars_allowable_chars_PERL_Bracket_Symbols(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/Grammar/SWI_vars/allowable_chars_PERL

            Test SWI_var characters setting as parameter to grammar.
            Expect:
            1) [Test Case]
                a) Audio newyork_newyork will be understood by grammar and SWI_meaning result expected to be "{"
                b) Audio newyork_newyork will be understood by grammar and SWI_meaning result expected to be "]"
                c) Audio newyork_newyork will be understood by grammar and SWI_meaning result expected to be "}"
                d) Audio newyork_newyork will be understood by grammar and SWI_meaning result expected to be "("
        """
        client = gRPCClient()
        #
        test_audio = "NRIR_newyork_newyork.wav"
        test_audio_format = 'pcm'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)

        # Test forward curly bracket
        test_grammar_data1 = 'NRIR_funky.xml?SWI_vars.char_val={'
        test_expect1 = '<SWI_meaning>{</SWI_meaning>'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes1)
        
        # Test square bracket
        test_grammar_data2 = 'NRIR_funky.xml?SWI_vars.char_val=]'
        test_expect2 = '<SWI_meaning>]</SWI_meaning>'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes2)

        # Test backward curly bracket
        test_grammar_data3 = 'NRIR_funky.xml?SWI_vars.char_val=}'
        test_expect3 = '<SWI_meaning>}</SWI_meaning>'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri3, mediaType=test_media_type)
        test_recogRes3 = [test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes3)

        # Test round bracket
        test_grammar_data4 = 'NRIR_funky.xml?SWI_vars.char_val=('
        test_expect4 = '<SWI_meaning>\(</SWI_meaning>'
        test_grammar_uri4 = client.test_res_url + test_grammar_data4
        test_recogRes4 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri4, mediaType=test_media_type)
        test_recogRes4 = [test_recogRes4]
        test_recInit4 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes4)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            #
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit2)
            time.sleep(1)
            #
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit3)
            time.sleep(1)
            #
            test_result4 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit4)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            msg += "Test recognition result 3: \n" + test_result4 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)
            self.assertRecognitionResult(inputToCheck=test_result4, expectResult=test_expect4)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test507_NRIR_osr20_feature_Grammar_SWI_vars_check_date_PERL(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/Grammar/SWI_vars/check_date_PERL 
        
        Simple test to see if we can constrain the date returned by the builtin date grammar
        within a range specified using the SWI_vars mechanism

        Expect:
        1) [Test Case]
            a) wednesday_feb_23_1999 and unrestricted date grammar. Expect result correct date "19990223".
            b) wednesday_feb_23_1994 and date grammar restricted with parameter SWI_vars.today=19980523. Expect result correct date "19940223".
            c) wednesday_feb_23_1999 and date grammar restricted with parameter SWI_vars.today=19980523. Expect corret date NOT IN RESULT.
        """
        client = gRPCClient()
        #
        test_audio_format = 'pcm'
        test_grammar_type = 'uri_grammar'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        #
        test_audio1 = "NRIR_wednesday_feb_23_1999.wav"
        test_grammar_data1 = 'NRIR_var_gram.xml'
        test_expect1 = '<SWI_meaning>19990223</SWI_meaning>'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes1)
        #
        test_audio2 = "NRIR_wednesday_feb_23_1994.wav"
        test_grammar_data2 = 'NRIR_var_gram.xml?SWI_vars.today=19980523'
        test_expect2 = '<SWI_meaning>19940223</SWI_meaning>'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes2)
        #
        test_audio3 = "NRIR_wednesday_feb_23_1999.wav"
        test_grammar_data3 = 'NRIR_var_gram.xml?SWI_vars.today=19980523'
        test_not_in_result3 = '<SWI_meaning>19990223</SWI_meaning>'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri3)
        test_recogRes3 = [test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes3)
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
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            #self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)
            self.assertNotRecognitionResult(inputToCheck=test_result3, undesiredResult=test_not_in_result3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test508_NRIR_osr20_feature_Grammar_SWI_vars_extra_info_PERL(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/Grammar/SWI_vars/extra_info_PERL 
        
        Simple test to see if we can use the SWI_vars mechanism to return 
        extra info with the result. In this case the grammar can recognize
        a city and state name returning only the city as SWI_meaning unless SWI_vars.want_state="yes"

        Expect:
        1) [Test Case]
            a) Audio sent "New York New York" with City_State grammar and default SWI_vars.want_state key. Expect only city "New York"
            b) Audio sent "Miami Florida" with City_State grammar and default SWI_vars.want_state key. Expect only city "Miami"
            c) Audio sent "New York New York" with City_State grammar and SWI_vars.want_state=yes. Expect city and state "New York New York"
            d) Audio sent "Miami Florida" with City_State grammar and SWI_vars.want_state=yes. Expect city and state "Miami Florida"
        """
        client = gRPCClient()
        #
        test_audio_format = 'pcm'
        test_grammar_type = 'uri_grammar'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        
        # "New York New York" only city
        test_audio1 = "NRIR_newyork_newyork.wav"
        test_grammar_data1 = 'NRIR_city_state.xml'
        test_expect1 = '<SWI_meaning>New York</SWI_meaning>'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes1)

        # "Miami Florida" only city
        test_audio2 = "NRIR_miami_florida.wav"
        test_grammar_data2 = 'NRIR_city_state.xml'
        test_expect2 = '<SWI_meaning>Miami</SWI_meaning>'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes2)

        # "New York New York" city and state
        test_audio3 = "NRIR_newyork_newyork.wav"
        test_grammar_data3 = 'NRIR_city_state.xml?SWI_vars.want_state=yes'
        test_expect3 = '<SWI_meaning>New York NY</SWI_meaning>'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri3)
        test_recogRes3 = [test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes3)

        # "Miami Florida" city and state
        test_audio4 = "NRIR_miami_florida.wav"
        test_grammar_data4 = 'NRIR_city_state.xml?SWI_vars.want_state=yes'
        test_expect4 = '<SWI_meaning>Miami FL</SWI_meaning>'
        test_grammar_uri4 = client.test_res_url + test_grammar_data4
        test_recogRes4 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri4)
        test_recogRes4 = [test_recogRes4]
        test_recInit4 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes4)
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio3, recInit=test_recInit3)
            time.sleep(1)
            test_result4 = client.qa_nr_recognize_test_func1(audioInput=test_audio4, recInit=test_recInit4)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            msg += "Test recognition result 4: \n" + test_result4 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)
            self.assertRecognitionResult(inputToCheck=test_result4, expectResult=test_expect4)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test509_NRIR_osr_quantum_feature_ContraintList_Constraints_3_0_9_3_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_3_0_9_3_PERL

        Test validates recognition of numbers using grammar and constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "three zero nine three"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_3_0_9_3.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_numbers.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_numbers_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "three zero nine three"

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test510_NRIR_osr_quantum_feature_ContraintList_Constraints_3_oh_9_3_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_3_oh_9_3_PERL

        Test validates recognition of numbers using grammar and constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "three oh nine three"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_3_oh_9_3.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_numbers.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_numbers_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "three oh nine three"

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test511_NRIR_osr_quantum_feature_ContraintList_Constraints_5_1_4_9_0_4_7_8_0_0_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_5_1_4_9_0_4_7_8_0_0_PERL

        Test validates recognition of numbers using grammar and constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "five one four nine zero four seven eight zero zero"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_5_1_4_9_0_4_7_8_0_0.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_numbers.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_numbers_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "five one four nine zero four seven eight zero zero"

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test512_NRIR_osr_quantum_feature_ContraintList_Constraints_5_1_4_9_oh_4_7_8_oh_oh_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_5_1_4_9_oh_4_7_8_oh_oh_PERL
        
        Test validates recognition of numbers using grammar and constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "five one four nine oh four seven eight oh oh"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_5_1_4_9_oh_4_7_8_oh_oh.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_numbers.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_numbers_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "five one four nine oh four seven eight oh oh"

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test513_NRIR_osr_quantum_feature_ContraintList_Constraints_Cuba_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_Cuba_PERL
        
        Test validates recognition of country/region using grammar and constraint list. The result is categorized by continents.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "Africa: Asia: AustraliaOceania: Continent: Europe: NorthAmerica: Cuba SouthAmerica:"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_Cuba.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_countries.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_country_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "\{Africa: Asia: AustraliaOceania: Continent: Europe: NorthAmerica: Cuba SouthAmerica:\}"

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test514_NRIR_osr_quantum_feature_ContraintList_Constraints_Egypt_Colombia_Paraguay_Egypt_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_Egypt_Colombia_Paraguay_Egypt_PERL

        Test validates recognition of country/region using grammar and constraint list. The result is categorized by continents.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "Africa: Egypt Egypt Asia: AustraliaOceania: Continent: Europe: NorthAmerica: SouthAmerica: Colombia Paraguay"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_Egypt_Colombia_Paraguay_Egypt.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_countries.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_country_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "\{Africa: Egypt Egypt Asia: AustraliaOceania: Continent: Europe: NorthAmerica: SouthAmerica: Colombia Paraguay\}"

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test515_NRIR_osr_quantum_feature_ContraintList_Constraints_Nepal_New_Zealand_Argentina_Ukraine_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_Nepal_New_Zealand_Argentina_Ukraine_PERL
        
        Test validates recognition of country/region using grammar and constraint list. The result is categorized by continents.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "Africa: Asia: Nepal AustraliaOceania: New Zealand Continent: Europe:  Ukraine NorthAmerica: SouthAmerica: Argentina"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_Nepal_New_Zealand_Argentina_Ukraine.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_countries.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_country_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "\{Africa: Asia: Nepal AustraliaOceania: New Zealand Continent: Europe:  Ukraine NorthAmerica: SouthAmerica: Argentina\}"

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test516_NRIR_osr_quantum_feature_ContraintList_Constraints_black_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_black_PERL
        
        Test validates recognition of colors using grammar and constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "black"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_black.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_colors.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_color_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "black"

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test517_NRIR_osr_quantum_feature_ContraintList_Constraints_black_blue_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_black_blue_PER
        
        Test validates recognition of colors using grammar and constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "black blue"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_black_blue.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_colors.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_color_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "black blue"

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test518_NRIR_osr_quantum_feature_ContraintList_Constraints_red_green_yellow_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_red_green_yellow_PER
        
        Test validates recognition of colors using grammar and constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "red green yellow"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_red_green_yellow.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_colors.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_color_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "red green yellow"

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test519_NRIR_osr_quantum_feature_ContraintList_Constraints_red_yellow_blue_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_red_yellow_blue_PERL
        
        Test validates recognition of colors using grammar and constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "red yellow blue"
        """
        client = gRPCClient()
        #
        #test_audio1 = "NRIR_red_yellow_blue.wav"
        test_audio1 = "NRIR_black_white.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_colors.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_color_constraints.txt'
        test_media_type1 = 'srgsxml'
        #test_expect1 = "red yellow blue"
        test_expect1 = "black white" 

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test520_NRIR_osr_quantum_feature_ContraintList_Weighted_black_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Weighted_black_PERL
        
        Test validates recognition of colors using grammar and weighted constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "black"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_black.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_colors.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_color_constraints_weighted_.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "black"

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test521_NRIR_osr_quantum_feature_ContraintList_Weighted_black_white_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Weighted_black_white_PERL
        
        Test validates recognition of colors using weighted grammar and weighted constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "black white"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_black_white.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_colors.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_color_constraints_weighted_.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "black white"

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test522_NRIR_osr_quantum_feature_ContraintList_Weighted_red_yellow_blue_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Weighted_red_yellow_blue_PERL
        
        Test validates recognition of colors using weighted grammar and weighted constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "red yellow blue"
        """
        client = gRPCClient()
        #
        #test_audio1 = "NRIR_red_yellow_blue.wav"
        test_audio1 = "NRIR_black_white.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_colors.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_color_constraints_weighted_.txt'
        test_media_type1 = 'srgsxml'
        #test_expect1 = "red yellow blue"
        test_expect1 = "black white"

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test523_NRIR_osr20_feature_Grammar_SWI_vars_uri_len_PERL(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/Grammar/SWI_vars/uri_len_PERL

            This tests long SWI_vars names and values.
            Expect:
            1) [Test Case]
                a) Short name. Expect successful recognition.
                b) Long value - limited by the MAX_LINE in rec_test (max length of command line is MAX_LINE-1, 2047 chars). Expect successful recognition.
                c) Long name. Expect successful recognition.
        """
        client = gRPCClient()
        test_audio_format = 'pcm'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_audio = "NRIR_newyork_newyork.wav"

        # Short name
        test_grammar_data1 = 'NRIR_uri_len.xml?SWI_vars.x=y'
        test_expect1 = "<SWI_meaning>SHORT_VAR y</SWI_meaning>"
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes1)

        # Long value - limited by the MAX_LINE in rec_test (max length of command line is MAX_LINE-1, 2047 chars)
        test_grammar_data2 = 'NRIR_uri_len.xml?SWI_vars.x=a_really_really_really_really_really_ridiculously_really_really_really_really_really_looooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong_value'
        test_expect2 = "<SWI_meaning>SHORT_VAR a_really_really_really_really_really_ridiculously_really_really_really_really_really_looooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong_value</SWI_meaning>"
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes2)
        
        # Long name
        test_grammar_data3 = 'NRIR_uri_len.xml?SWI_vars.a_really_really_really_really_really_really_really_really_really_really_loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong_name=z'
        test_expect3 = "<SWI_meaning>LONG_VAR z</SWI_meaning>"
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri3, mediaType=test_media_type)
        test_recogRes3 = [test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes3)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit3)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
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

    def test524_NRIR_osr20_feature_ConstraintWeight_ConstraintWeight_basic_PERL(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/ConstraintWeight/ConstraintWeight_basic_PERL

            Verify basic functionality of weights on alphanum constraints
            Expect:
            1) [Test Case]
                a) Execute a simple alphanum recognition with unweighted constraints and builtin alphanum grammar. Expect "m3h5m5".
                b) Repeat the recognition but this time use weighted constraints so that the result should be different than before. Expect "m3h5n5"
                c) Repeat step 1 in order to make sure all is well. Expect "m3h5m5".

            ignored parameters:
            - swirec_load_adjusted_speedvsaccuracy set to busy
        """
        client = gRPCClient()
        
        test_audio = "NRIR_ogiad1002_utt001.ulaw"
        test_audio_format = 'ulaw'
        test_media_type = 'srgsxml'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)

        # 1. Execute a simple alphanum recognition with unweighted constraints
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'alphanum?entries=' + client.test_res_url + 'NRIR_const-plain.txt'
        test_expect1 = "m3h5m5"
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes1)

        # 2. Repeat the recognition but this time use weighted constraints so that the result should be different than before.
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'alphanum?entries=' + client.test_res_url + 'NRIR_const-weighted.txt'
        test_expect2 = "m3h5n5"
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2, mediaType=test_media_type)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes2)
        
        # 3. Repeat step 1 in order to make sure all is well.
        test_grammar_type3 = 'builtin'
        test_grammar_data3 = 'alphanum?entries=' + client.test_res_url + 'NRIR_const-plain.txt'
        test_expect3 = "m3h5m5"
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_data3, mediaType=test_media_type)
        test_recogRes3 = [test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes3)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit3)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
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

    def test525_NRIR_proton_feature_completetimeout_ctimeout_precedence_1_PERL(self):
        """
        NR IR Converted testcases:
            ./proton_feature/completetimeout/ctimeout_precedence_1_PERL

        Tests precedence "set completetimeout in a grammar <meta> tag" over setting as Recognition Parameter.

        Expect:
        1) [Test Case]
            a) Audio: "January the first <1300ms silence> 2005". Completetimeout: set in Grammar 1000ms, set as Recognition Parameter 0ms. Expect recognition result "january the first two_thousand five".
            b) Audio: "Januay the first <300ms silence> 2005 <1300ms silence>". Completetimeout: set in Grammar 600ms, set in Recognition Parameter 100ms. Expect recognition result "january the first".

        parameters ignored:
            - SWIrecAcousticStateReset theRec
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_jan1st_silence_1300ms_2005.wav"
        test_audio_format1 = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_date_ctimeout_1000ms.xml'
        test_media_type1 = 'srgsxml'
        test_completeTimeout1 = 0
        test_expect1 = ">january the first two_thousand five<"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1, completeTimeout=test_completeTimeout1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        test_audio2 = "NRIR_jan1st_silence_300ms_2005_silence_1300ms.wav"
        test_audio_format2 = 'pcm'
        test_grammar_type2 = 'uri_grammar'
        test_grammar_data2 = 'NRIR_date_ctimeout_600ms.xml'
        test_media_type2 = 'srgsxml'
        test_completeTimeout2 = 100
        test_expect2 = ">january the first<"

        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        test_recogParams2 = client.recognition_parameters(audioFormat=test_audio_format2, completeTimeout=test_completeTimeout2)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams2, recogRes=test_recogRes2)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(2)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            #
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test526_NRIR_spectrum_feature_model_combination_test_1st_pass_model_combination_PERL(self):
        """
        NR IR Converted testcases:
            ./spectrum_feature/model_combination/test_1st_pass_model_combination_PERL

        Test model combination parameters have NO effects on score diffence for 1st pass recognition.
        Set parameters in grammar meta tags. Use same audio "NRIR_time.wav"
        Extract SWI_rawScore from recognition results and compare to other results. Expect all SWI_rawScore to be equal.

        Expect:
        1) [Test Case]
            a) step1: set swirec_model_combination=false;swirec_model_combination_fp_weight=0.4. Extract SWI_rawScore.
            b) step2: set swirec_model_combination=true;swirec_model_combination_fp_weight=0. Extract SWI_rawScore should be equal to step1.
            c) step3: set swirec_model_combination=true;swirec_model_combination_fp_weight=0.4. Extract SWI_rawScore should be equal to step1.
            d) step4: set swirec_model_combination=true;swirec_model_combination_fp_weight=0.8. Extract SWI_rawScore should be equal to step1.

        parameters ignored:
            - SWIrecAcousticStateReset theRec
            - swirec_load_adjusted_speedvsaccuracy idle
        """
        client = gRPCClient()
        #
        test_audio = "NRIR_time.wav"
        test_audio_format = 'pcm'
        test_incompleteTimeout = 1000
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format, incompleteTimeout=test_incompleteTimeout)
        test_grammar_type = 'uri_grammar'
        test_grammar_data = 'NRIR_parameter_grammar_swirec_extra_nbest_keys_SWI_rawScore.grxml'
        test_media_type = 'xswiparameter'
        test_grammar_uri = client.test_res_url + test_grammar_data
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        
        # step1: set swirec_model_combination=false;swirec_model_combination_fp_weight=0.4
        test_expect1 = "three fifty four p_m"
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_time_false_04.grxml'
        test_media_type1 = 'srgsxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogRes_1 = [test_recogRes, test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_1)
        
        # step2: set swirec_model_combination=true;swirec_model_combination_fp_weight=0
        test_expect2 = "three fifty four p_m"
        test_grammar_type2 = 'uri_grammar'
        test_grammar_data2 = 'NRIR_time_true_0.grxml'
        test_media_type2 = 'srgsxml'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        test_recogRes_2 = [test_recogRes, test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_2)
        
        # step3: set swirec_model_combination=true;swirec_model_combination_fp_weight=0.4
        test_expect3 = "three fifty four p_m"
        test_grammar_type3 = 'uri_grammar'
        test_grammar_data3 = 'NRIR_time_true_04.grxml'
        test_media_type3 = 'srgsxml'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_uri3, mediaType=test_media_type3)
        test_recogRes_3 = [test_recogRes, test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_3)

        # step4: set swirec_model_combination=true;swirec_model_combination_fp_weight=0.8
        test_expect4 = "three fifty four p_m"
        test_grammar_type4 = 'uri_grammar'
        test_grammar_data4 = 'NRIR_time_true_08.grxml'
        test_media_type4 = 'srgsxml'
        test_grammar_uri4 = client.test_res_url + test_grammar_data4
        test_recogRes4 = client.recognition_resource(grammarType=test_grammar_type4, grammarData=test_grammar_uri4, mediaType=test_media_type4)
        test_recogRes_4 = [test_recogRes, test_recogRes4]
        test_recInit4 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_4)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit3)
            time.sleep(1)
            test_result4 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit4)
            time.sleep(1)
            
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            msg += "Test recognition result 4: \n" + test_result4 + "\n"
            #
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)
            self.assertRecognitionResult(inputToCheck=test_result4, expectResult=test_expect4)
            
            # All SWI_rawScore should be equal.
            rawScore1 = float(self.getFirstXmlOccurrence(xmlTarget="SWI_rawScore", result=test_result1))
            rawScore2 = float(self.getFirstXmlOccurrence(xmlTarget="SWI_rawScore", result=test_result2))
            rawScore3 = float(self.getFirstXmlOccurrence(xmlTarget="SWI_rawScore", result=test_result3))
            rawScore4 = float(self.getFirstXmlOccurrence(xmlTarget="SWI_rawScore", result=test_result4))
            self.assertEquals(rawScore1, rawScore2)
            self.assertEquals(rawScore1, rawScore3)
            self.assertEquals(rawScore1, rawScore4)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test527_NRIR_spectrum_feature_model_combination_test_2nd_pass_model_combination_1_PERL(self):
        """
        NR IR Converted testcases:
            ./spectrum_feature/model_combination/test_2nd_pass_model_combination_1_PERL

        Test model combination parameters have NO effects on score diffence for 2nd pass recognition.
        Set parameters in grammar meta tags. Use same audio "NRIR_digits.wav"
        Extract SWI_rawScore from recognition results and compare to other results. Expect all SWI_rawScore to be equal.

        Expect:
        1) [Test Case]
            a) step1: set swirec_model_combination=false; swirec_model_combination_fp_weight=0.Extract SWI_rawScore.
            b) step2: set swirec_model_combination=false; swirec_model_combination_fp_weight=0.4. Extract SWI_rawScore should be equal to step1.
            c) step3: set swirec_model_combination=false; swirec_model_combination_fp_weight=0.7. Extract SWI_rawScore should be equal to step1.

        parameters ignored:
            - SWIrecAcousticStateReset theRec
            - swirec_load_adjusted_speedvsaccuracy idle
        """
        client = gRPCClient()
        #
        test_audio = "NRIR_digits.wav"
        test_audio_format = 'pcm'
        test_incompleteTimeout = 1000
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format, incompleteTimeout=test_incompleteTimeout)
        test_grammar_type = 'uri_grammar'
        test_grammar_data = 'NRIR_parameter_grammar_swirec_extra_nbest_keys_SWI_rawScore.grxml'
        test_media_type = 'xswiparameter'
        test_grammar_uri = client.test_res_url + test_grammar_data
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)

        # step1: set swirec_model_combination=false; swirec_model_combination_fp_weight=0
        test_expect1 = "one zero eight six one three"
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_digits_false_0.grxml'
        test_media_type1 = 'srgsxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogRes_1 = [test_recogRes, test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_1)
        
        # step2: set swirec_model_combination=false; swirec_model_combination_fp_weight=0.4
        test_expect2 = "one zero eight six one three"
        test_grammar_type2 = 'uri_grammar'
        test_grammar_data2 = 'NRIR_digits_false_04.grxml'
        test_media_type2 = 'srgsxml'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        test_recogRes_2 = [test_recogRes, test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_2)
        
        # step3: set swirec_model_combination=false; swirec_model_combination_fp_weight=0.7
        test_expect3 = "one zero eight six one three"
        test_grammar_type3 = 'uri_grammar'
        test_grammar_data3 = 'NRIR_digits_false_07.grxml'
        test_media_type3 = 'srgsxml'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_uri3, mediaType=test_media_type3)
        test_recogRes_3 = [test_recogRes, test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_3)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit3)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            #
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)
            
            # All SWI_rawScore should be equal.
            rawScore1 = float(self.getFirstXmlOccurrence(xmlTarget="SWI_rawScore", result=test_result1))
            rawScore2 = float(self.getFirstXmlOccurrence(xmlTarget="SWI_rawScore", result=test_result2))
            rawScore3 = float(self.getFirstXmlOccurrence(xmlTarget="SWI_rawScore", result=test_result3))
            self.assertEquals(rawScore1, rawScore2)
            self.assertEquals(rawScore1, rawScore3)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test528_NRIR_spectrum_feature_model_combination_test_2nd_pass_model_combination_2_PERL(self):
        """
        NR IR Converted testcases:
            ./spectrum_feature/model_combination/test_2nd_pass_model_combination_2_PERL

        Test model combination parameters have NO effects on score diffence for 2nd pass recognition.
        Set parameters in grammar meta tags. Use same audio "NRIR_digits.wav"
        Extract SWI_rawScore from recognition results and compare to other results. Expect all SWI_rawScore to be equal.

        Expect:
        1) [Test Case]
            a) step1: set swirec_model_combination=false; swirec_model_combination_fp_weight=0.8. Extract SWI_rawScore from result.
            b) step2: set swirec_model_combination=true; swirec_model_combination_fp_weight=0. Extract SWI_rawScore should be equal to step1.

        parameters ignored:
            - SWIrecAcousticStateReset theRec
            - swirec_load_adjusted_speedvsaccuracy idle
        """
        client = gRPCClient()
        #
        test_audio = "NRIR_digits.wav"
        test_audio_format = 'pcm'
        test_incompleteTimeout = 1000
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format, incompleteTimeout=test_incompleteTimeout)
        test_grammar_type = 'uri_grammar'
        test_grammar_data = 'NRIR_parameter_grammar_swirec_extra_nbest_keys_SWI_rawScore.grxml'
        test_media_type = 'xswiparameter'
        test_grammar_uri = client.test_res_url + test_grammar_data
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)

        # step1: swirec_model_combination=false; swirec_model_combination_fp_weight=0.8
        test_expect1 = "one zero eight six one three"
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_digits_false_08.grxml'
        test_media_type1 = 'srgsxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogRes_1 = [test_recogRes, test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_1)
        
        # step2: set swirec_model_combination=true; swirec_model_combination_fp_weight=0
        test_expect2 = "one zero eight six one three"
        test_grammar_type2 = 'uri_grammar'
        test_grammar_data2 = 'NRIR_digits_true_0.grxml'
        test_media_type2 = 'srgsxml'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        test_recogRes_2 = [test_recogRes, test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_2)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit2)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            #
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            # All SWI_rawScore should be equal.
            rawScore1 = float(self.getFirstXmlOccurrence(xmlTarget="SWI_rawScore", result=test_result1))
            rawScore2 = float(self.getFirstXmlOccurrence(xmlTarget="SWI_rawScore", result=test_result2))
            self.assertEquals(rawScore1, rawScore2)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test529_NRIR_osr20_feature_Grammar_SWI_vars_parallel_grammars_PERL(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/Grammar/SWI_vars/parallel_grammars_PERL

        Test SWI_vars with parallel grammars under the following scenarios:
        1. activate the same grammar twice with different SWI_var values
        2. activate the different grammars with the same SWI_var variable name

        Expect:
        1) [Test Case]
            a) date grammar restricted with parameter SWI_vars.today=19980523.
                i)  wednesday_feb_23_1994 Expect result correct date "19940223".
                ii) wednesday_feb_23_1999 Expect correct date NOT IN RESULT.
            b) date grammar restricted with parameter SWI_vars.today=20000523.
                i)  wednesday_feb_23_1999 Expect result correct date "19990223".
            c) date grammar restricted with parameter SWI_vars.today=20000523.
                i)  wednesday_feb_23_1994 Expect result correct date "19940223".
                ii) wednesday_feb_23_1999 Expect result correct date "19990223".
        """
        client = gRPCClient()
        
        # Today set to 1998/05/23
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_var_gram.xml?SWI_vars.today=19980523'
        test_media_type1 = 'srgsxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogRes_1 = [test_recogRes1]
        test_audio_format1 = 'pcm'
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes_1)
        # Date from 1994 should be a valid parse.
        test_audio11 = "NRIR_wednesday_feb_23_1994.wav"
        test_expect11 = "19940223"
        # Date from 1999 should not be a valid parse.
        test_audio12 = "NRIR_wednesday_feb_23_1999.wav"
        test_not_in_result12 = "19990223"
        
        # Today set to 1998/05/23
        test_grammar_type2 = 'uri_grammar'
        test_grammar_data2 = 'NRIR_var_gram.xml?SWI_vars.today=20000523'
        test_media_type2 = 'srgsxml'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        test_recogRes_2 = [test_recogRes2]
        test_audio_format2 = 'pcm'
        test_recogParams2 = client.recognition_parameters(audioFormat=test_audio_format2)
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams2, recogRes=test_recogRes_2)
        # Date from 1999 should be a valid parse.
        test_audio21 = "NRIR_wednesday_feb_23_1999.wav"
        test_expect21 = "19990223"

        # Load grammar twice each time with different today parameter. Reuse the Recognition Resource form previous steps.
        test_grammar_type3 = 'uri_grammar'
        test_grammar_data3 = 'NRIR_var_gram2.xml?SWI_vars.today=20000523'
        test_media_type3 = 'srgsxml'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_uri3, mediaType=test_media_type3)
        test_recogRes_3 = [test_recogRes2, test_recogRes3]
        test_audio_format3 = 'pcm'
        test_recogParams3 = client.recognition_parameters(audioFormat=test_audio_format3)
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams3, recogRes=test_recogRes_3)
        # Date from 1994 should be a valid parse.
        test_audio31 = "NRIR_wednesday_feb_23_1994.wav"
        test_expect31 = "19940223"
        # Date from 1999 should be a valid parse.
        test_audio32 = "NRIR_wednesday_feb_23_1999.wav"
        test_expect32 = "19990223"
        
        try:
            #
            test_result11 = client.qa_nr_recognize_test_func1(audioInput=test_audio11, recInit=test_recInit1)
            time.sleep(1)
            test_result12 = client.qa_nr_recognize_test_func1(audioInput=test_audio12, recInit=test_recInit1)
            time.sleep(1)
            test_result21 = client.qa_nr_recognize_test_func1(audioInput=test_audio21, recInit=test_recInit2)
            time.sleep(1)
            test_result31 = client.qa_nr_recognize_test_func1(audioInput=test_audio31, recInit=test_recInit3)
            time.sleep(1)
            test_result32 = client.qa_nr_recognize_test_func1(audioInput=test_audio32, recInit=test_recInit3)
            time.sleep(1)
            
            msg = ""
            msg += "Test recognition result 1: \n" + test_result11 + "\n"
            msg += "Test recognition result 2: \n" + test_result12 + "\n"
            msg += "Test recognition result 3: \n" + test_result21 + "\n"
            msg += "Test recognition result 4: \n" + test_result31 + "\n"
            msg += "Test recognition result 5: \n" + test_result32 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result11, expectResult=test_expect11)
            self.assertNotRecognitionResult(inputToCheck=test_result11, undesiredResult=test_not_in_result12)
            self.assertRecognitionResult(inputToCheck=test_result21, expectResult=test_expect21)
            self.assertRecognitionResult(inputToCheck=test_result31, expectResult=test_expect31)
            self.assertRecognitionResult(inputToCheck=test_result32, expectResult=test_expect32)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test530_NRIR_osr_quantum_feature_ConstraintList_scripts_3_0_9_3_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/scripts/3_0_9_3_PERL 
        
        Test validates recognition of numbers using grammar and constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "three zero nine three"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_3_0_9_3.wav"
        test_audio_format1 = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_3_0_9_3.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_numbers_constraints.txt' 
        test_media_type1 = 'srgsxml'
        test_expect1 = "three zero nine three"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test531_NRIR_osr_quantum_feature_ConstraintList_Constraints_3_5_7_0_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_3_5_7_0_PERL
        
        Test validates recognition of numbers using grammar and constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "three five seven zero"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_3_5_7_0.wav"
        test_audio_format1 = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_numbers.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_numbers_constraints.txt' 
        test_media_type1 = 'srgsxml'
        test_expect1 = "three five seven zero"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test532_NRIR_osr_quantum_feature_ConstraintList_Constraints_3_5_7_oh_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_3_5_7_oh_PERL
        
        Test validates recognition of numbers using grammar and constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "three five seven oh"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_3_5_7_oh.wav"
        test_audio_format1 = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_numbers.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_numbers_constraints.txt' 
        test_media_type1 = 'srgsxml'
        test_expect1 = "three five seven oh"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test533_NRIR_osr_quantum_feature_ConstraintList_Constraints_5_1_4_9_0_4_7_8_oh_0_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_5_1_4_9_0_4_7_8_oh_0_PERL
        
        Test validates recognition of numbers using grammar and constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "five one four nine zero four seven eight oh zero"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_5_1_4_9_0_4_7_8_oh_0.wav"
        test_audio_format1 = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_numbers.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_numbers_constraints.txt' 
        test_media_type1 = 'srgsxml'
        test_expect1 = "five one four nine zero four seven eight oh zero"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test534_NRIR_osr_quantum_feature_ConstraintList_Constraints_5_1_4_9_oh_4_7_8_0_0_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_5_1_4_9_oh_4_7_8_0_0_PERL
        
        Test validates recognition of numbers using grammar and constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "five one four nine oh four seven eight zero zero"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_5_1_4_9_oh_4_7_8_0_0.wav"
        test_audio_format1 = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_numbers.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_numbers_constraints.txt' 
        test_media_type1 = 'srgsxml'
        test_expect1 = "five one four nine oh four seven eight zero zero"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test535_NRIR_osr_quantum_feature_ConstraintList_Constraints_Albania_Colombia_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_Albania_Colombia_PERL
        
        Test validates recognition of country/region using grammar and constraint list. The result is categorized by continents.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "Africa: Asia: AustraliaOceania: Continent: Europe:  Albania NorthAmerica: SouthAmerica: Colombia"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_Albania_Colombia.wav"
        test_audio_format1 = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_countries.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_country_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "\{Africa: Asia: AustraliaOceania: Continent: Europe:  Albania NorthAmerica: SouthAmerica: Colombia\}"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test536_NRIR_osr_quantum_feature_ConstraintList_Constraints_Brazil_Paraguay_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_Brazil_Paraguay_PERL
        
        Test validates recognition of country/region using grammar and constraint list. The result is categorized by continents.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "Africa: Asia: AustraliaOceania: Continent: Europe: NorthAmerica: SouthAmerica: Brazil Paraguay"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_Brazil_Paraguay.wav"
        test_audio_format1 = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_countries.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_country_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "\{Africa: Asia: AustraliaOceania: Continent: Europe: NorthAmerica: SouthAmerica: Brazil Paraguay\}"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test537_NRIR_osr_quantum_feature_ConstraintList_Constraints_Denmark_Macedonia_Brazil_Venezuela_The_Bahamas_Saint_Kitts_and_Nevis_China_Russia_Chad_Ivory_Coast_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_Denmark_Macedonia_Brazil_Venezuela_The_Bahamas_Saint_Kitts_and_Nevis_China_Russia_Chad_Ivory_Coast_PERL
        
        Test validates recognition of country/region using grammar and constraint list. The result is categorized by continents.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "Africa: Chad Asia: China AustraliaOceania: Continent: Europe:  Denmark Russia NorthAmerica: The Bahamas Saint Kitts and Nevis SouthAmerica: Brazil Venezuela"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_Denmark_Macedonia_Brazil_Venezuela_The_Bahamas_Saint_Kitts_and_Nevis_China_Russia_Chad_Ivory_Coast.wav"
        test_audio_format1 = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_countries.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_country_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "\{Africa: Chad .+ Asia: China AustraliaOceania: Continent: Europe:  Denmark  .+  Russia NorthAmerica: The Bahamas Saint Kitts and Nevis SouthAmerica: Brazil Venezuela\}"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test538_NRIR_osr_quantum_feature_ConstraintList_Constraints_Hungary_Paraguay_Togo_Singapore_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_Hungary_Paraguay_Togo_Singapore_PERL
        
        Test validates recognition of country/region using grammar and constraint list. The result is categorized by continents.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "Africa: Togo Asia: Singapore AustraliaOceania: Continent: Europe:  Hungary NorthAmerica: SouthAmerica: Paraguay"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_Hungary_Paraguay_Togo_Singapore.wav"
        test_audio_format1 = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_countries.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_country_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "\{Africa: Togo Asia: Singapore AustraliaOceania: Continent: Europe:  Hungary NorthAmerica: SouthAmerica: Paraguay\}"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test539_NRIR_osr_quantum_feature_ConstraintList_Constraints_Italy_France_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_Italy_France_PERL
        
        Test validates recognition of country/region using grammar and constraint list. The result is categorized by continents.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "Africa: Asia: AustraliaOceania: Continent: Europe:  Italy  France NorthAmerica: SouthAmerica:"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_Italy_France.wav"
        test_audio_format1 = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_countries.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_country_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "\{Africa: Asia: AustraliaOceania: Continent: Europe:  Italy  France NorthAmerica: SouthAmerica:\}"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test540_NRIR_osr_quantum_feature_ConstraintList_Constraints_Liechtenstein_French_Guiana_Tonga_Philippines_Mozambique_Cyprus_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_Liechtenstein_French_Guiana_Tonga_Philippines_Mozambique_Cyprus_PERL
        
        Test validates recognition of country/region using grammar and constraint list. The result is categorized by continents.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "Africa: Mozambique Asia: Philippines AustraliaOceania: Tonga Continent: Europe:  Liechtenstein  Cyprus NorthAmerica: SouthAmerica: French Guiana"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_Liechtenstein_French_Guiana_Tonga_Philippines_Mozambique_Cyprus.wav"
        test_audio_format1 = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_countries.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_country_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "\{Africa: Mozambique Asia: Philippines AustraliaOceania: Tonga Continent: Europe:  Liechtenstein  Cyprus NorthAmerica: SouthAmerica: French Guiana\}"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test541_NRIR_osr_quantum_feature_ConstraintList_Constraints_Micronesia_Bangladesh_Egypt_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_Micronesia_Bangladesh_Egypt_PERL
        
        Test validates recognition of country/region using grammar and constraint list. The result is categorized by continents.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "Africa: Egypt Asia: Bangladesh AustraliaOceania: Micronesia Continent: Europe: NorthAmerica: SouthAmerica:"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_Micronesia_Bangladesh_Egypt.wav"
        test_audio_format1 = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_countries.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_country_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "\{Africa: Egypt Asia: Bangladesh AustraliaOceania: Micronesia Continent: Europe: NorthAmerica: SouthAmerica:\}"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test542_NRIR_osr_quantum_feature_ConstraintList_Constraints_black_white_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_black_white_PERL
        
        Test validates recognition of colors using grammar and constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "black white"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_black_white.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_colors.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_color_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "black white"

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test543_NRIR_osr_quantum_feature_ConstraintList_Constraints_blue_green_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_blue_green_PERL
        
        Test validates recognition of colors using grammar and constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "blue green"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_blue_green.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_colors.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_color_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "blue green"

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test544_NRIR_osr_quantum_feature_ConstraintList_Constraints_red_green_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_red_green_PER
        
        Test validates recognition of colors using grammar and constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "red green"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_red_green.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_colors.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_color_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "red green"

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test545_NRIR_osr_quantum_feature_ConstraintList_Constraints_white_black_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Constraints_white_black_PER
        
        Test validates recognition of colors using grammar and constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "white black"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_white_black.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_colors.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_color_constraints.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "white black"

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test546_NRIR_osr_quantum_feature_ConstraintList_Weighted_black_blue_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Weighted_black_blue_PERL
        
        Test validates recognition of colors using grammar and weighted constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "black blue"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_black_blue.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_colors.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_color_constraints_weighted_.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "black blue"

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test547_NRIR_osr_quantum_feature_ConstraintList_Weighted_red_green_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Weighted_red_green_PERL
        
        Test validates recognition of colors using grammar and weighted constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "red green"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_red_green.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_colors.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_color_constraints_weighted_.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "red green"

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test548_NRIR_osr_quantum_feature_ConstraintList_Weighted_red_green_yellow_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/ConstraintList/Weighted_red_green_yellow_PERL
        
        Test validates recognition of colors using grammar and weighted constraint list.
        Expect:
        1) [Test Case]
            a) Load grammar and constraint list. Expect successful audio recognition "red green yellow"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_red_green_yellow.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_colors.xml?SWI_param.constraintlist=' + client.test_res_url + 'NRIR_color_constraints_weighted_.txt'
        test_media_type1 = 'srgsxml'
        test_expect1 = "red green yellow"

        test_grammar_uri = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type1)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes1]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test549_NRIR_proton_feature_completetimeout_ctimeout_multiple_grammar_PERL(self):
        """
        NR IR Converted testcases:
            ./proton_feature/completetimeout/ctimeout_multiple_grammar_PERL

        Test completetimeout parameter while loading multiple grammars for each recognition.
        Expect:
        1) [Test case] 
            a) set completetimeout in a grammar <meta> tag. 
                i)  date completetimeout = 700ms. Expect ">january the first two_thousand five<"
                ii) digit completetiemout = 300ms. Expect ">zero one<"
            b) set completetimeout in a grammar <meta> tag.
                i)  date completetimeout = 300ms. Expect ">january the first<"
                ii) digit completetiemout = 700ms. Expect ">zero one two three<"
        """
        client = gRPCClient()
        # Set grammars for step 1) a)
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_date_ctimeout_700ms.xml'
        test_media_type1 = 'srgsxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)        
        test_grammar_type2 = 'uri_grammar'
        test_grammar_data2 = 'NRIR_digits_ctimeout_300ms.xml'
        test_media_type2 = 'srgsxml'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2, mediaType=test_media_type2)

        test_audio_format1 = 'pcm'
        test_completeTimeout1 = 'ignore'
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1, completeTimeout=test_completeTimeout1)
        test_recogRes_1 = [test_recogRes1, test_recogRes2]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes_1)
        # 1) a) i)
        test_audio11 = "NRIR_jan1st_silence_600ms_2005.wav"
        test_expect11 = ">january the first two_thousand five<"
        # 1) a) ii)
        test_audio12 = "NRIR_01_silence_500ms_23.wav"
        test_expect12 = ">zero one<"

        # Set grammars for step 1) b)
        test_grammar_type3 = 'uri_grammar'
        test_grammar_data3 = 'NRIR_date_ctimeout_300ms.xml'
        test_media_type3 = 'srgsxml'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_uri3, mediaType=test_media_type3)        
        test_grammar_type4 = 'uri_grammar'
        test_grammar_data4 = 'NRIR_digits_ctimeout_700ms.xml'
        test_media_type4 = 'srgsxml'
        test_grammar_uri4 = client.test_res_url + test_grammar_data4
        test_recogRes4 = client.recognition_resource(grammarType=test_grammar_type4, grammarData=test_grammar_uri4, mediaType=test_media_type4)

        test_audio_format2 = 'pcm'
        test_completeTimeout2 = 'ignore'
        test_recogParams2 = client.recognition_parameters(audioFormat=test_audio_format2, completeTimeout=test_completeTimeout2)
        test_recogRes_2 = [test_recogRes3, test_recogRes4]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams2, recogRes=test_recogRes_2)
        # 1) b) i)
        test_audio21 = "NRIR_jan1st_silence_600ms_2005.wav"
        test_expect21 = ">january the first<"
        # 1) b) ii)
        test_audio22 = "NRIR_01_silence_500ms_23.wav"
        test_expect22 = ">zero one two three<"

        try:
            #
            test_result11 = client.qa_nr_recognize_test_func1(audioInput=test_audio11, recInit=test_recInit1)
            time.sleep(1)
            test_result12 = client.qa_nr_recognize_test_func1(audioInput=test_audio12, recInit=test_recInit1)
            time.sleep(2)
            test_result21 = client.qa_nr_recognize_test_func1(audioInput=test_audio21, recInit=test_recInit2)
            time.sleep(1)
            test_result22 = client.qa_nr_recognize_test_func1(audioInput=test_audio22, recInit=test_recInit2)
            time.sleep(2)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result11 + "\n"
            msg += "Test recognition result 2: \n" + test_result12 + "\n"
            msg += "Test recognition result 3: \n" + test_result21 + "\n"
            msg += "Test recognition result 4: \n" + test_result22 + "\n"
            # self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result11, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result12, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result21, expectResult=test_expect21)
            self.assertRecognitionResult(inputToCheck=test_result22, expectResult=test_expect22)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
    
    def test551_NRIR_spectrum_feature_NLU_meaning_mask_meaning_mask_format_1_PERL(self):
        """
        NR IR Converted testcases:
            ./spectrum_feature/NLU_meaning_mask/meaning_mask_format_1_PERL

        Test NLU-setting Meaning Mask meaning list format correct format of SWI.internalSSMMask=<ssm_file>:<enable=0|1>:<meaning list>.
        All recognitions have parameter grammar swirec_extra_nbest_keys set to "SWI_literal SWI_rawScore SWI_spoken SWI_grammarName SWI_meaning SWI_load_adjusted_speedvsaccuracy"
        Same grammar and audio for all recognitions, the keys vary.
        Expect:
        1) [Test Case]
            a) meaning list <x,y> enable=0 grxml wrapper grammar. Expect in result: "TONIGHT", "TOMORROW", "YESTERDAY"
            b) meaning list *<x> enable=0. Expect in result: "TONIGHT", "DUMMY"
            b) meaning list <x>* enable=1 gram wrapper grammar. Expect in result: "TONIGHT", "TOMORROW", "TODAY"

        parameter ignored:
        - swirec_load_adjusted_speedvsaccuracy busy
        - SWIrecAcousticStateReset REC
        - ssm_num_meanings_out = 5 because NRC gives error "Unknown parameter name 'ssm_num_meanings_out'"
        """
        client = gRPCClient()
        
        test_audio_format = 'ulaw'
        test_grammar_type = 'uri_grammar'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_audio = "NRIR_sleet_and_snow_ulaw_audio.ulaw"
        
        # set parameter via parameter grammar: swirec_extra_nbest_keys "SWI_literal SWI_rawScore SWI_spoken SWI_grammarName SWI_meaning SWI_load_adjusted_speedvsaccuracy"
        test_grammar_data = "NRIR_swirec_extra_nbest_keys_6.grxml"
        test_media_type = 'xswiparameter'
        test_grammar_uri = client.test_res_url + test_grammar_data
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)

        # meaning list <x,y> enable=0 grxml wrapper grammar. Expect in result: "TONIGHT", "TOMORROW", "YESTERDAY"
        test_grammar_data1 = 'NRIR_Test_GramSSM.grxml?SWI.internalSSMMask=Test_SSM.ssm:0:DUMMY,TODAY'
        test_media_type1 = 'srgsxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogRes1 = [test_recogRes, test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes1)
        test_expect11 = "TONIGHT"
        test_expect12 = "TOMORROW"
        test_expect13 = "YESTERDAY"

        # meaning list *<x> enable=0. Expect in result: "TONIGHT", "DUMMY"
        test_grammar_data2 = 'NRIR_Test_GramSSM.grxml?SWI.internalSSMMask=Test_SSM.ssm:0:*DAY,*RROW'
        test_media_type2 = 'srgsxml'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        test_recogRes2 = [test_recogRes, test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes2)
        test_expect21 = "TONIGHT"
        test_expect22 = 'DUMMY'

        # meaning list <x>* enable=1 gram wrapper grammar. Expect in result: "TONIGHT", "TOMORROW", "TODAY"
        test_grammar_data3 = 'NRIR_Test_GramSSM.gram?SWI.internalSSMMask=Test_SSM.ssm:1:TO*'
        test_media_type3 = 'xswigrammar'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri3, mediaType=test_media_type3)
        test_recogRes3 = [test_recogRes, test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes3)
        test_expect31 = "TONIGHT"
        test_expect32 = 'TOMORROW'
        test_expect33 = 'TODAY'
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit3)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect13)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect21)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect22)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect31)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect32)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect33)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test552_NRIR_spectrum_feature_NLU_meaning_mask_meaning_mask_format_2_PERL(self):
        """
        NR IR Converted testcases:
            ./spectrum_feature/NLU_meaning_mask/meaning_mask_format_1_PERL

        Test NLU-setting Meaning Mask meaning list format correct format of SWI.internalSSMMask=<ssm_file>:<enable=0|1>:<meaning list>.
        All recognitions have parameter grammar swirec_extra_nbest_keys set to "SWI_literal SWI_rawScore SWI_spoken SWI_grammarName SWI_meaning SWI_load_adjusted_speedvsaccuracy"
        Same grammar and audio for all recognitions, the keys vary.
        Expect:
        1) [Test Case]
            a) wrong format - ssm_file does not exist. Expect "DUMMY", "TONIGHT", "TOMORROW", "TODAY", "YESTERDAY"
            b) wrong format - wrong enable. Expect in result: "DUMMY", "TONIGHT", "TOMORROW", "TODAY", "YESTERDAY"
            b) wrong format - there are 2 or more identical SSM file name, the format check will fail. Expect in result: "DUMMY", "TONIGHT", "TOMORROW", "TODAY", "YESTERDAY"

        parameter ignored:
        - swirec_load_adjusted_speedvsaccuracy busy
        - SWIrecAcousticStateReset REC
        - ssm_num_meanings_out = 5 because NRC gives error "Unknown parameter name 'ssm_num_meanings_out'"
        """
        client = gRPCClient()
        
        test_audio_format = 'ulaw'
        test_grammar_type = 'uri_grammar'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_audio = "NRIR_sleet_and_snow_ulaw_audio.ulaw"
        
        # set parameter via parameter grammar: swirec_extra_nbest_keys "SWI_literal SWI_rawScore SWI_spoken SWI_grammarName SWI_meaning SWI_load_adjusted_speedvsaccuracy"
        test_grammar_data = "NRIR_swirec_extra_nbest_keys_6.grxml"
        test_media_type = 'xswiparameter'
        test_grammar_uri = client.test_res_url + test_grammar_data
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)

        # wrong format - ssm_file does not exist. Expect "DUMMY", "TONIGHT", "TOMORROW", "TODAY", "YESTERDAY"
        test_grammar_data1 = 'NRIR_Test_GramSSM.grxml?SWI.internalSSMMask=Nonexist.ssm:0:DUMMY,TO*,*DAY'
        test_media_type1 = 'srgsxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogRes1 = [test_recogRes, test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes1)
        test_expect11 = "TONIGHT"
        test_expect12 = "TOMORROW"
        test_expect13 = "YESTERDAY"
        test_expect14 = "TODAY"
        test_expect15 = "DUMMY"

        # wrong format - wrong enable. Expect in result: "DUMMY", "TONIGHT", "TOMORROW", "TODAY", "YESTERDAY"
        test_grammar_data2 = 'NRIR_Test_GramSSM.grxml?SWI.internalSSMMask=Test_SSM.ssm:0:*DAY,*RROW'
        test_media_type2 = 'srgsxml'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        test_recogRes2 = [test_recogRes, test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes2)
        test_expect21 = "TONIGHT"
        test_expect22 = "TOMORROW"
        test_expect23 = "YESTERDAY"
        test_expect24 = "TODAY"
        test_expect25 = "DUMMY"

        # wrong format - there are 2 or more identical SSM file name, the format check will fail. Expect in result: "DUMMY", "TONIGHT", "TOMORROW", "TODAY", "YESTERDAY"
        test_grammar_data3 = 'NRIR_Test_GramSSM.grxml?SWI.internalSSMMask=Test_SSM.ssm:0:DUMMY,TO*,*DAY|Test_SSM.ssm:1:DUMMY,TO*,*DAY*'
        test_media_type3 = 'srgsxml'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri3, mediaType=test_media_type3)
        test_recogRes3 = [test_recogRes, test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes3)
        test_expect31 = "TONIGHT"
        test_expect32 = "TOMORROW"
        test_expect33 = "YESTERDAY"
        test_expect34 = "TODAY"
        test_expect35 = "DUMMY"
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit3)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect13)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect14)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect15)
            #
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect21)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect22)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect23)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect24)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect25)
            #
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect31)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect32)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect33)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect34)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect35)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test554_NRIR_spectrum_feature_NLU_meaning_mask_meaning_mask_smoke_2_ssm_PERL(self):
        """
        NR IR Converted testcases:
            ./spectrum_feature/NLU_meaning_mask/meaning_mask_smoke_2_ssm_PERL

        Smoke test NLU-setting Meaning Mask with 2ssm
        make sure grammar URI contained mask info
        correct format of SWI.internalSSMMask=<ssm_file1>:<enable=0|1>:<meaning list>|<ssm_file2>:<enable=0|1>:<meaning list>
        All recognitions have parameter grammar swirec_extra_nbest_keys set to "SWI_literal SWI_rawScore SWI_spoken SWI_grammarName SWI_meaning SWI_load_adjusted_speedvsaccuracy"
        Same grammar and audio for all recognitions, the keys vary.
        Expect:
        1) [Test Case]
            a) no meaning mask specified. Expect in result: "Test_SSM_Sensitive_Chars-DUMMY", "Test_SSM_Sensitive_Chars-TO,NIGHT", "Test_SSM_Sensitive_Chars-TO~RROW", "Test_SSM_Sensitive_Chars-TO|DAY", "Test_SSM_Sensitive_Chars-YESTER:DAY",
                      "Test_SSM-DUMMY", "Test_SSM-TONIGHT", "Test_SSM-TOMORROW", "Test_SSM-TODAY", "Test_SSM-YESTERDAY"
            b) ssm file1 mask enable=1 ssm file2 maske enable=1. "Test_SSM_Sensitive_Chars-TO,NIGHT", "Test_SSM_Sensitive_Chars-TO~RROW", "Test_SSM_Sensitive_Chars-TO|DAY", "Test_SSM_Sensitive_Chars-YESTER:DAY",
                      "Test_SSM-DUMMY", "Test_SSM-TOMORROW", "Test_SSM-TODAY","Test_SSM-TONIGHT"
            b) ssm file1 mask enable=1 ssm file2 maske enable=0. Expect in result: "Test_SSM_Sensitive_Chars-TO,NIGHT", "Test_SSM_Sensitive_Chars-TO~RROW", "Test_SSM_Sensitive_Chars-TO|DAY", "Test_SSM_Sensitive_Chars-YESTER:DAY",
                      "Test_SSM-DUMMY", "Test_SSM-TONIGHT", "Test_SSM-TOMORROW"

        parameter ignored:
        - swirec_load_adjusted_speedvsaccuracy idle
        - SWIrecAcousticStateReset REC
        - ssm_num_meanings_out = 5 because NRC gives error "Unknown parameter name 'ssm_num_meanings_out'"
        """
        client = gRPCClient()
        
        test_audio_format = 'ulaw'
        test_grammar_type = 'uri_grammar'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_audio = "NRIR_sleet_and_snow_ulaw_audio.ulaw"
        
        # set parameter via parameter grammar: swirec_extra_nbest_keys "SWI_literal SWI_rawScore SWI_spoken SWI_grammarName SWI_meaning SWI_load_adjusted_speedvsaccuracy"
        test_grammar_data = "NRIR_swirec_extra_nbest_keys_6.grxml"
        test_media_type = 'xswiparameter'
        test_grammar_uri = client.test_res_url + test_grammar_data
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        #
        test_grammar_data1 = 'NRIR_Test_GramSSM_2_ssm.grxml'
        test_media_type1 = 'srgsxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogRes1 = [test_recogRes, test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes1)
        test_expect11 = "DUMMY"         # Test_SSM_Sensitive_Chars
        test_expect12 = "TO,NIGHT"      # Test_SSM_Sensitive_Chars
        test_expect13 = "TO~RROW"       # Test_SSM_Sensitive_Chars
        test_expect14 = "TO|DAY"        # Test_SSM_Sensitive_Chars
        test_expect15 = "YESTER:DAY"    # Test_SSM_Sensitive_Chars
        test_expect16 = "DUMMY"         # Test_SSM
        test_expect17 = "TONIGHT"       # Test_SSM
        test_expect18 = "TOMORROW"      # Test_SSM
        test_expect19 = "TODAY"         # Test_SSM
        test_expect110 = "YESTERDAY"    # Test_SSM
        #
        test_grammar_data2 = 'NRIR_Test_GramSSM_2_ssm.grxml?SWI.internalSSMMask=Test_SSM_Sensitive_Chars.ssm:1:TO\\|DAY,TO\\,NIGHT,YESTER\\:DAY,TO\\~RROW|Test_SSM.ssm:0:*DAY'
        test_media_type2 = 'srgsxml'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        test_recogRes2 = [test_recogRes, test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes2)
        test_expect21 = "TO,NIGHT"      # Test_SSM_Sensitive_Chars
        test_expect22 = "TO~RROW"       # Test_SSM_Sensitive_Chars
        test_expect23 = "TO|DAY"        # Test_SSM_Sensitive_Chars
        test_expect24 = "YESTER:DAY"    # Test_SSM_Sensitive_Chars
        test_expect25 = "DUMMY"         # Test_SSM
        test_expect26 = "TOMORROW"      # Test_SSM
        test_expect27 = "TODAY"         # Test_SSM
        test_expect28 = "TONIGHT"       # Test_SSM
        #
        test_grammar_data3 = 'NRIR_Test_GramSSM_2_ssm.grxml?SWI.internalSSMMask=Test_SSM_Sensitive_Chars.ssm:0:TO\\|DAY,TO\\,NIGHT,YESTER\\:DAY,TO\\~RROW|Test_SSM.ssm:0:*DAY'
        test_media_type3 = 'srgsxml'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri3, mediaType=test_media_type3)
        test_recogRes3 = [test_recogRes, test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes3)
        test_expect31 = "TO,NIGHT"      # Test_SSM_Sensitive_Chars
        test_expect32 = "TO~RROW"       # Test_SSM_Sensitive_Chars
        test_expect33 = "TO|DAY"        # Test_SSM_Sensitive_Chars
        test_expect34 = "YESTER:DAY"    # Test_SSM_Sensitive_Chars 
        test_expect35 = "DUMMY"         # Test_SSM
        test_expect36 = "TOMORROW"      # Test_SSM
        test_expect37 = "TONIGHT"       # Test_SSM
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit3)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect13)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect14)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect15)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect16)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect17)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect18)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect19)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect110)
            #
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect21)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect22)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect23)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect24)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect25)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect26)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect27)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect28)
            #
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect31)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect32)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect33)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect34)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect35)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect36)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect37)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()


    def test049_Recognition_secure_context_level_suppress_uri_grammar(self):
        """
        Test NRC recognition secure_context_level parameter when set to SUPPRESS with audio 'yes.ulaw' and uri grammar
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Manual validation] verify NRC utterance from this case via QA NRC scripts (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results SUPPRESSED in the diagnostic logs.
            b) No utterance waveforms are recorded & playable from this test (user input utterance), such as: NUAN-xx-xx-nrc-xxxxxxx-krwcs-xxxxxxxxx-utt01-PLAYABLE.wav
        3) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results SUPPRESSED in the call logs.
                Event "SWIrcnd" should have tokens SECURE=TRUE, RSTT=ok, ENDR=eeos, RSLT=_SUPPRESSED, RAWT=_SUPPRESSED, SPOK=_SUPPRESSED, KEYS=_SUPPRESSED, WVNM=_SUPPRESSED, MPNM=en.us/10.0.2/models/FirstPass/models.hmm
                Event "SWIrslt" should have tokens SECURE=TRUE, MEDIA=application/x-vnd.speechworks.emma+xml, CNTNT=_SUPPRESSED 
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = 'yes.ulaw'
        test_grammar = "uri_grammar_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        test_secureContextLevel = 'SUPPRESS'
        test_expect1 = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        
        test_recogParams1 = client.recognition_parameters(secureContextLevel=test_secureContextLevel)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams1, recogRes=test_recogRes1)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit1, expected_result=test_expect1, secure_clog=True)
        test_record_1.set_checklist_types(["Recognition", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="ok")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="ENDR", value="eeos")
        test_record_1.add_token_to_checklist(evnt="NUANwvfm", token="PLAYABLE", value="_SUPPRESSED")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RSLT", value="_SUPPRESSED")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RAWT", value="_SUPPRESSED")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="SPOK", value="_SUPPRESSED")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="KEYS", value="_SUPPRESSED")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="WVNM", value="_SUPPRESSED")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="MPNM", value="en.us/10.0.2/models/FirstPass/models.hmm")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="SECURE", value="TRUE")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="MEDIA", value="application/x-vnd.speechworks.emma+xml")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="_SUPPRESSED")

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            #
            kafka.validate_callLogs(test_record_1)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()


    def test050_Recognition_secure_context_level_suppress_noMatch(self):
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
        test_secureContextLevel = 'SUPPRESS'
        test_expect = "NO_MATCH"

        test_recogParams = client.recognition_parameters(secureContextLevel=test_secureContextLevel)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, result_status="NO_MATCH", secure_clog=True)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_undesired_to_checklist("SWIrslt")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="ENDR", value="eeos")
        test_record_1.add_token_to_checklist(evnt="NUANwvfm", token="PLAYABLE", value="_SUPPRESSED")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RSLT", value="_SUPPRESSED")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RAWT", value="_SUPPRESSED")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="SPOK", value="_SUPPRESSED")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="KEYS", value="_SUPPRESSED")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="WVNM", value="_SUPPRESSED")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="MPNM", value="en.us/10.0.2/models/FirstPass/models.hmm")

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
