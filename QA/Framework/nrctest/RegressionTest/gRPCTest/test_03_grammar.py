from hashlib import sha256
import sys
import os
import time

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
class NRCTestGrammar(TestFixture):
   

    def test001_BuiltinGrammarGeneric(self):
        """
        Test NRC recognition Builtin grammar with 945015260 'one.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld
        3) [Manual validation] 
            a) waveform logging (file) found and playable (user input utterance), such as: NUAN-xx-xx-nrc-xxxxxxx-krwcs-xxxxxxxxx-utt01-PLAYABLE.wav
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = "945015260.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)    
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test002_InlineGrammarOne(self):
        """
        Test NRC recognition inline grammar with audio 'one.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld
        3) [Manual validation] 
            a) waveform logging (file) found and playable (user input utterance), such as: NUAN-xx-xx-nrc-xxxxxxx-krwcs-xxxxxxxxx-utt01-PLAYABLE.wav
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = 'one.ulaw'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_one\"> <rule id=\"yes_one\" scope=\"public\">\n<one-of>\n<item>one</item>\n<item>yes</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>one</SWI_literal>.+<SWI_meaning.+one.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=en-US")

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

    def test003_InlineGrammarYes(self):
        """
          Test NRC recognition inline grammar with audio 'one.ulaw'
          Expect:
          1) [Test case] NRC recognize return successful
        """
        client = gRPCClient()
        
        test_audio = 'yes.ulaw'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type = 'srgsxml'
        test_grammar_type = 'inline_grammar'
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)   
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test004_UriGrammarYes(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld
        3) [Manual validation] 
            a) waveform logging (file) found and playable (user input utterance), such as: NUAN-xx-xx-nrc-xxxxxxx-krwcs-xxxxxxxxx-utt01-PLAYABLE.wav
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = 'yes.ulaw'
        test_grammar = "uri_grammar_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"" + test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
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

    def test005_InvalidUriGrammar(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return should not be successful with return code as 400
        2) [Manual validation] verify NRC call log & utterance from this case via QA NRC call logging support & scripts (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related all events presented in the call log, including:  SWIldst, SWIgcst, SWIgrld, SWIgcnd, SWIifst, SWIifnd SWIldnd;
        """
        client = gRPCClient()
        
        test_audio = 'yes.ulaw'
        test_grammar = "xxxx.grxml"     # invalid / wrong uri grammar path
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        
        try:
        
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            print(msg)    
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            time.sleep(20)

    def test006_BuiltinGrammarDigit(self):
        """
        Test NRC recognition Builtin Digit grammar with audio '1.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld; value of Token URI should be builtin:grammar/digits
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "1.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(3)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test007_BuiltinGrammarBoolean(self):
        """
        Test NRC recognition Builtin Boolean grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld; value of Token URI should be builtin:grammar/boolean
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "yes.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'boolean'
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/boolean.+<instance>true<\/instance.+\/interpretation.+\/result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/boolean")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/boolean")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test008_BuiltinGrammarDate(self):
        """
        Test NRC recognition Builtin Date grammar with audio 'date_dt0204f_date26.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld; value of Token URI should be builtin:grammar/date
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "date_dt0204f_date26.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'date'
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/date.+<instance>19940223<\/instance.+\/interpretation.+\/result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/date")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/date")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test009_BuiltinGrammarTime1(self):
        """
        Test NRC recognition Builtin Time grammar with audio 'six_am.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld; value of Token URI should be builtin:grammar/time
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "six_am.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'time'
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/time.+<instance>0600a<\/instance.+\/interpretation.+\/result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/time")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/time")
        
        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0010_BuiltinGrammarTime2(self):
        """
        Test NRC recognition Builtin Time grammar with audio 'six_fifty_pm.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        """

        client = gRPCClient()

        test_audio = "six_fifty_pm.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'time'
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/time.*<instance>0650p<\/instance.+\/interpretation.+\/result>"

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0011_BuiltinGrammarPhone(self):
        """
        Test NRC recognition Builtin Phone grammar with audio '451782342135.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld; value of Token URI should be builtin:grammar/phone
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "451782342135.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'phone'
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/phone.+<instance>4517822421<\/instance.+\/interpretation.+\/result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/phone")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/phone")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0012_BuiltinGrammarCurrency(self):
        """
        Test NRC recognition Builtin Currency grammar with audio 'currency_dt0207f_dlramt25.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld; value of Token URI should be builtin:grammar/currency
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "currency_dt0207f_dlramt25.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'currency'
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/currency.+<instance>47270.21<\/instance.+\/interpretation.+\/result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/currency")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/currency")

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0013_BuiltinGrammarNumber(self):
        """
        Test NRC recognition Builtin Number grammar with audio 'num_NRSA3000037_utt043.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld; value of Token URI should be builtin:grammar/number
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "num_NRSA3000037_utt043.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'number'
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/number.+<instance>70<\/instance.+\/interpretation.+\/result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/number")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/number")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)
            time.sleep(3)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0014_BuiltinGrammarAlphanum(self):
        """
        Test NRC recognition Builtin alphanum grammar with audio 'alphanum_m385m5.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld; value of Token URI should be builtin:grammar/alphanum
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "alphanum_m385m5.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'alphanum'
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/alphanum.+<instance>m385m5<\/instance.+\/interpretation.+\/result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/alphanum")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/alphanum")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()


    # This is negative test case for builtin grammar

    def test0015_BuiltinGrammarInvalidGrammarData(self):
        """
        Test NRC recognition Builtin alphanum grammar with audio 'alphanum_m385m5.ulaw'
        Expect:
        1) [Test case] NRC recognize return should not be successful with rerun status code as 400
            
         """  
        
        client = gRPCClient()

        test_audio = "one.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'Invalid'

        test_result = ""
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource"
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            time.sleep(20)

    def test0016_InlineGrammarAutomaticMediaType(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw' & SRGS Xml MediaType
        Expect:
        1) [Test case] NRC recognize return should be successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) for event SWIrcst, value of Token GRMT should be application/srgs+xml     
         """ 
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'
        test_grammar_type = 'inline_grammar'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type = None
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/srgs+xml")
        test_record_1.add_event_to_checklist(event="EVNT", value="SWIgrld")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0017_InlineGrammarSrgsxmlMediaType(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw' & SRGS Xml MediaType
        Expect:
        1) [Test case] NRC recognize return should be successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) for event SWIrcst, value of Token GRMT should be application/srgs+xml     
         """ 
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'
        test_grammar_type = 'inline_grammar'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type = 'srgsxml'
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/srgs+xml")
        test_record_1.add_event_to_checklist(event="EVNT", value="SWIgrld")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0018_InlineGrammarInvalidGrammarData(self):
        """
        Test NRC recognition Inline grammar with audio 'one.ulaw'
        Expect:
        1) [Test case] NRC recognize return should not be successful with rerun status code as 400
            
        """

        client = gRPCClient()

        test_audio = 'one.ulaw'
        test_grammar_type = 'inline_grammar'
        # test_grammar value is not valid here see xmlns
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http3://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>one</item>\n<item>yes</item>\n</one-of>\n</rulrrrrre>\n</grammar2>\n"
        test_media_type = 'srgsxml'

        test_result = ""

        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource"
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            time.sleep(20)


    def test0019_InlineGrammarInvalidMediaType(self):
        """
        Test NRC recognition Inline grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return should not be successful with rerun status code as 400
            
        """

        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar_type = 'inline_grammar'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type = 'Invalid'
        test_expect = 'unknown enum label \"Invalid\"'

        try:
            test_recogParams = client.recognition_parameters()
            test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type)

        except (AssertionError, TimeoutException, Exception) as e:
            msg = "\nFound exception!\n" + str(e)
            # print(msg)
            if self.assertRecognitionResult(inputToCheck=str(e), expectResult=test_expect):
                msg = "Test passed. Expected: \n" + msg + "\n"
                print(msg)
            else:
                self.fail(e)    

            
    def test0020_UriGrammarAutomaticMediaType(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw' & Automatic MediaType
        Expect:
        1) [Test case] NRC recognize return should be successful
            
         """ 

        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar = "uri_grammar_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = None
        test_grammar_uri = client.test_res_url + test_grammar
        print("Test grammar URI: " + test_grammar_uri + "\n")
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0021_UriGrammarSrgsxmlMediaType(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw' & SRGS Xml MediaType
        Expect:
        1) [Test case] NRC recognize return should be successful    
         """ 

        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar = "uri_grammar_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        print("Test grammar URI: " + test_grammar_uri + "\n")
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0022_UriGrammarInvalidMediaType(self):
        """
            Test NRC recognition URI grammar with audio 'yes.ulaw' & InlvalidMediaType
            Expect:
            1) [Test case] NRC recognize return should not be successful with return code as 400
        """

        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar = "uri_grammar_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'Invalid'
        test_expect4 = 'unknown enum label \"Invalid\"'
        test_grammar_uri = client.test_res_url + test_grammar
   
        try:
            test_recogParams = client.recognition_parameters()
            test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type)

        except (AssertionError, TimeoutException, Exception) as e:
            msg = "\nFound exception!\n" + str(e)
            # print(msg)
            if self.assertRecognitionResult(inputToCheck=str(e), expectResult=test_expect4):
                msg = "Test passed. Expected: \n" + msg + "\n"
                print(msg)
            else:
                self.fail(e)

    def test0023_InvalidGrammarType(self):
        """
        Test NRC recognition Invalid grammar with audio 'one.ulaw'
        Expect:
        1) [Test case] NRC recognize return should not be successful with return code as 400
        """ 
        client = gRPCClient()

        test_audio = 'one.ulaw'
        test_grammar_type = "Invalid_Type"
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http3://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>one</item>\n<item>yes</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type = 'srgsxml'
        test_result = ""
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            time.sleep(20)

    def test0024_BuiltinGrammarNLSMLResultFormat(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw' & SRGS Xml MediaType
        Expect:
        1) [Test case] NRC recognize return should be successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
                a) Grammar related events all presented in the call log, including: SWIgrld;
                b) for event SWIrslt, value of Token MEDIA should be application/x-vnd.speechworks.emma+xml
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "yes.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'boolean'
        test_audio_format = 'ulaw'
        test_result_format = 'nlsml'
        test_recogParams = client.recognition_parameters()
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format,resultFormat=test_result_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/boolean.+<instance>true<\/instance.+\/interpretation.+\/result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="MEDIA", value="application/x-vnd.speechworks.emma+xml")
        test_record_1.add_event_to_checklist(event="EVNT", value="SWIgrld")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/boolean")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0025_BuiltinGrammarEMMAResultFormat(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw' & EMMA result format
        Expect:
        1) [Test case] NRC recognize return should be successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) for event SWIrslt, value of Token MEDIA should be application/x-vnd.nuance.emma+xml
        """ 
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "yes.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'boolean'
        test_audio_format = 'ulaw'
        test_result_format = 'emma'
        #test_recogParams = client.recognition_parameters()
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format,resultFormat=test_result_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "<emma:emma.*builtin:grammar\/boolean.*<emma:literal>true<\/emma:literal><\/emma:interpretation><\/emma:emma>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="MEDIA", value="application/x-vnd.nuance.emma+xml")
        test_record_1.add_event_to_checklist(event="EVNT", value="SWIgrld")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="builtin:grammar\/boolean")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)    # for debug validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0026_InlineGrammarNLSMLResultFormat(self):
        """
            Test NRC recognition Inline grammar with audio 'yes.ulaw' & NLSML result format
            Expect:
            1) [Test case] NRC recognize return should be successful
        """ 

        client = gRPCClient()
        test_audio = 'yes.ulaw'
        test_audio_format = 'ulaw'
        test_result_format = 'nlsml'
        test_grammar_type = 'inline_grammar'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type = 'srgsxml'
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format,resultFormat=test_result_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0027_InlineGrammarEMMAResultFormat(self):
        
        """
            Test NRC recognition Inline grammar with audio 'yes.ulaw' & EMMA result format
            Expect:
            1) [Test case] NRC recognize return should be successful
         """ 

        client = gRPCClient()
        test_audio = 'yes.ulaw'
        test_audio_format = 'ulaw'
        test_result_format = 'emma'
        test_grammar_type = 'inline_grammar'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type = 'srgsxml'

        test_expect = "<emma:emma.*{SWI_literal:yes}<\/SWI_meaning><\/emma:interpretation><\/emma:emma>"
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format,resultFormat=test_result_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0028_URIGrammarNLSMLResultFormat(self):
        
        """
            Test NRC recognition URI grammar with audio 'yes.ulaw' & NLSML result format
            Expect:
            1) [Test case] NRC recognize return should be successful
         """ 

        client = gRPCClient()

        test_expect = "<result><interpretation grammar=.*{SWI_literal:yes}<\/SWI_meaning><\/instance.+\/interpretation.+\/result>"

        test_audio = 'yes.ulaw'
        test_audio_format = 'ulaw'
        test_result_format = 'nlsml'
        test_grammar = "uri_grammar_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'

        test_grammar_uri = client.test_res_url + test_grammar
        print("Test grammar URI: " + test_grammar_uri + "\n")
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format,resultFormat=test_result_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0029_URIGrammarEMMAResultFormat(self):
        
        """
            Test NRC recognition URI grammar with audio 'yes.ulaw' & EMMA result format
            Expect:
            1) [Test case] NRC recognize return should be successful
        """

        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_audio_format = 'ulaw'
        test_result_format = 'emma'
        test_grammar = "uri_grammar_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'

        test_grammar_uri = client.test_res_url + test_grammar
        print("Test grammar URI: " + test_grammar_uri + "\n")

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format,resultFormat=test_result_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_expect = "<emma:emma.*{SWI_literal:yes}<\/SWI_meaning><\/emma:interpretation><\/emma:emma>"
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0030_BuiltinGrammarId(self):
    
        """
            Test NRC recognition URI grammar with audio 'yes.ulaw' & EMMA result format
            Expect:
            1) [Test case] NRC recognize return should be successful
         """ 
        client = gRPCClient()

        test_audio = "1.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_grammar_Id = 'builtin_digits'
        test_expect = "<result><interpretation grammar=.*" + test_grammar_Id + ".*<instance>1<\/instance.+\/interpretation.+\/result>"
        # test_expect = "INVALID"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data,grammarId=test_grammar_Id)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0031_InlineGrammarId(self):  
        """
            Test NRC recognition URI grammar with audio 'yes.ulaw' & EMMA result format
            Expect:
            1) [Test case] NRC recognize return should be successful
        """
        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar_type = 'inline_grammar'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type = 'srgsxml'
        test_grammar_Id = 'Inline_yes_no'
        test_expect = "<?xml.+><result><interpretation grammar=.*" + test_grammar_Id + ".*confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,mediaType=test_media_type, grammarId=test_grammar_Id)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,recInit=test_recInit)
            #
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()


    def test0032_UriGrammarId(self):
          
        """
            Test NRC recognition URI grammar with audio 'yes.ulaw' & EMMA result format
            Expect:
            1) [Test case] NRC recognize return should be successful
         """ 

        client = gRPCClient()
        
        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_yes.grxml"
        
        test_media_type = 'srgsxml'
        test_grammar_Id = 'grammar_uri_yes'
        test_grammar_uri = client.test_res_url + test_grammar
        #print("Test grammar URI: " + test_grammar_uri + "\n")
       
        test_expect = "<?xml.+><result><interpretation grammar=.*" +test_grammar_Id+ ".*confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type, grammarId = test_grammar_Id)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        
        try:
            
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print("Expected "+test_expect)
            print(msg)    
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup() 

    def test0033_BuiltinGrammarWeight(self):
        """
            Test NRC recognition Builtin grammar with audio 'yes.ulaw' & Grammar Weight as 2
            Expect:
            1) [Test case] NRC recognize return should be successful
            2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
                a) Grammar related events all presented in the call log, including: SWIgrld;
                b) for event SWIgrld, value of Token WGHT should be matched with value of grammar weight
        """ 
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "1.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_grammar_weight = 2
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data,grammarWeight=test_grammar_weight)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="WGHT", value=test_grammar_weight)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0034_InlineGrammarWeight(self):
        """
        Test NRC recognition Inline grammar with audio 'yes.ulaw' & Grammar Weight as 2
        Expect:
        1) [Test case] NRC recognize return should be successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) for event SWIgrld, value of Token WGHT should be matched with value of grammar weight.
        """ 
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'
        test_grammar_type = 'inline_grammar'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type = 'srgsxml'
        test_grammar_weight = 2
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,mediaType=test_media_type, grammarWeight=test_grammar_weight)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=en-US")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="WGHT", value=test_grammar_weight)
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0035_UriGrammarWeight(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw' & Grammar Weight as 2
        Expect:
        1) [Test case] NRC recognize return should be successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
                a) Grammar related events all presented in the call log, including: SWIgrld;
                b) for event SWIgrld, value of Token WGHT should be matched with value of grammar weight.
        """  
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_yes.grxml"
        test_media_type = 'srgsxml'
        test_grammar_weight = 2
        test_grammar_uri = client.test_res_url + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters()
        # Specifies the grammar's weight relative to other grammars active for that recognition. This value can range from 1 to 32767. Default is 1
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,mediaType=test_media_type, grammarWeight=test_grammar_weight)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="WGHT", value=test_grammar_weight)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\""+test_grammar_uri)
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0036_BuiltinGrammarInvalidWeight(self):
        """
          Test NRC recognition Buitin grammar with audio '1.ulaw' and Invalid Grammar weight
          Expect:
          1) [Test case] NRC recognize return should not be successful wit return status code as 400
        
         """ 
        client = gRPCClient()

        test_audio = "1.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_grammar_weight = 32768

        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Grammar weight is out of range."

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data,grammarWeight=test_grammar_weight)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0037_InlineGrammarInvalidWeight(self):
        """
          Test NRC recognition Buitin grammar with audio '1.ulaw' and Invalid Grammar weight
          Expect:
          1) [Test case] NRC recognize return should not be successful wit return status code as 400
        
         """ 

        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar_type = 'inline_grammar'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type = 'srgsxml'

        test_grammar_weight = 32768
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Grammar weight is out of range."
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,mediaType=test_media_type, grammarWeight=test_grammar_weight)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0038_UriGrammarInvalidWeight(self):
        """
          Test NRC recognition Buitin grammar with audio '1.ulaw' and Invalid Grammar weight
          Expect:
          1) [Test case] NRC recognize return should not be successful wit return status code as 400
        
         """ 

        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_yes.grxml"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        test_grammar_weight = 32768
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Grammar weight is out of range."
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,mediaType=test_media_type, grammarWeight=test_grammar_weight)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0039_UriGrammarParametersRequestTimeout(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw' & URI Prameter requestTimeout as 10000
        Expect:
        1) [Test case] NRC recognize return should be successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
                a) Grammar related events all presented in the call log, including: SWIgrld;
                b) for all the grammar related events value of Token PROPS should contain inet.timeoutDownload=10000;inet.timeoutIO=10000;inet.timeoutOpen=10000 
         """ 
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_yes.grxml"
        test_media_type = 'srgsxml'

        test_requestTimeout = 10000
        test_grammar_uri = client.test_res_url + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        test_UriParams = client.recognition_UriGrammarParam(requestTimeout=test_requestTimeout)
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type, uriParameters=test_UriParams)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_event_to_checklist(event="EVNT", value="SWIgrld")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="inet.timeoutDownload=10000;inet.timeoutIO=10000;inet.timeoutOpen=10000")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\""+test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0040_UriGrammarParametersShortRequestTimeout(self):
    
        """
            Test NRC recognition URI grammar with audio 'yes.ulaw' & URI Prameter requestTimeout as 2
            Expect:
            1) [Test case] NRC recognize return should be successful
         """ 

        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_oui_fr - CA.grxml"
        # "uri_grammar_yes.grxml"
        test_media_type = 'srgsxml'
        test_requestTimeout = 2
        test_grammar_uri = client.test_res_url + test_grammar
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource "
        test_UriParams = client.recognition_UriGrammarParam(requestTimeout=test_requestTimeout)
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,mediaType=test_media_type, uriParameters=test_UriParams)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            time.sleep(20)

    def test0041_UriGrammarParametersContentBase(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw' & URI Prameter content base
        Expect:
        1) [Test case] NRC recognize return should be successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
                a) Grammar related events all presented in the call log, including: SWIgrld;
                b) for all the grammar related events value of Token PROPS should contain inet.urlBase=client.test_res_url
         """ 
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_yes.grxml"
        test_media_type = 'srgsxml'
        test_contentBase = client.test_res_url
        # test_grammar_uri = client.test_res_url + test_grammar
        test_grammar_uri = test_grammar

        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        # test_UriParams =  client.recognition_UriGrammarParam(requestTimeout=0, contentBase=test_contentBase, maxAge=0, maxStale=0)
        test_UriParams = client.recognition_UriGrammarParam(contentBase=test_contentBase)
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type, uriParameters=test_UriParams)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_event_to_checklist(event="EVNT", value="SWIgrld")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="inet.urlBase="+client.test_res_url)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\""+test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0042_UriGrammarParametersInvalidContentBase(self):

        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_yes.grxml"
        test_media_type = 'srgsxml'
        # invalid base uri(grammar is not present)
        test_contentBase = 'XXX'
        # test_grammar_uri = client.test_res_url + test_grammar
        test_grammar_uri = test_grammar

        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource "
        test_UriParams = client.recognition_UriGrammarParam(contentBase=test_contentBase)
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type, uriParameters=test_UriParams)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            time.sleep(20)

    def test0043_UriGrammarParametersMaxAgeDefault(self):

        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_yes.grxml"
        test_media_type = 'srgsxml'

        test_maxAge = 0
        test_grammar_uri = client.test_res_url + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        # test_UriParams =  client.recognition_UriGrammarParam(requestTimeout=0, contentBase=test_contentBase, maxAge=0, maxStale=0)
        test_UriParams = client.recognition_UriGrammarParam(maxAge=test_maxAge)
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type, uriParameters=test_UriParams)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0044_UriGrammarParametersMaxAge(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw' & URI Prameter Max Age as 5
        Expect:
        1) [Test case] NRC recognize return should be successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) for all the grammar related events value of Token PROPS should contain net.maxage=5
        """ 
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_yes.grxml"
        test_media_type = 'srgsxml'
        test_maxAge = 5
        test_grammar_uri = client.test_res_url + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        # test_UriParams =  client.recognition_UriGrammarParam(requestTimeout=0, contentBase=test_contentBase, maxAge=0, maxStale=0)
        test_UriParams = client.recognition_UriGrammarParam(maxAge=test_maxAge)
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type, uriParameters=test_UriParams)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_event_to_checklist(event="EVNT", value="SWIgrld")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="net.maxage=5")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\""+test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0045_UriGrammarParametersMaxStaleDefault(self):

        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_yes.grxml"
        test_media_type = 'srgsxml'
        test_maxStale = 0
        test_grammar_uri = client.test_res_url + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        test_UriParams = client.recognition_UriGrammarParam(maxStale=test_maxStale)
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type, uriParameters=test_UriParams)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0046_UriGrammarParametersMaxStale(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw' & URI Prameter Max Stale as 5
        Expect:
        1) [Test case] NRC recognize return should be successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) for all the grammar related events value of Token PROPS should contain net.maxstale=5
         """ 
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_yes.grxml"
        test_media_type = 'srgsxml'
        test_maxStale = 5
        test_grammar_uri = client.test_res_url + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        test_UriParams = client.recognition_UriGrammarParam(maxStale=test_maxStale)
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,mediaType=test_media_type, uriParameters=test_UriParams)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_event_to_checklist(event="EVNT", value="SWIgrld")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="net.maxstale=5")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\""+test_grammar_uri)

        try:    
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test047_InvalidInlineGrammar(self):
        """
        Test NRC uri grammar (yes) on QA Apache server with audio input yes.ulaw
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        
        test_audio = 'yes.ulaw'
        test_grammar = "<?xml version=\"1.0\"?>xxxxxx</grammar>\n"
        test_media_type = 'srgsxml'
        test_grammar_type = 'inline_grammar'
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource"
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            time.sleep(20)

    def test0048_InlineGrammarXswigrammarMediaType(self):

        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar_type = 'inline_grammar'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type = 'xswigrammar'
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
   
    def test0049_UriGrammarXswigrammarMediaType(self):

        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar = "uri_grammar_yes.gram"
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'
        test_grammar_uri = client.test_res_url + test_grammar
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0050_UriGrammarXswigrammarMediaTypefrCA(self):

        client = gRPCClient()
        
        test_audio = 'oui.wav'
        test_audio_format = 'pcm'
        test_language = 'fr-CA'
        test_media_type = 'xswigrammar'
        test_grammar = "uri_grammar_oui_fr-CA.gram"
        test_grammar_type = "uri_grammar"
        test_grammar_uri = client.test_res_url + test_grammar
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>oui</SWI_literal>.+<SWI_meaning.+oui.+SWI_meaning></instance></interpretation></result>"
        
        try:
            
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  
           
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
                        
    def test0051_UriGrammarXswiparameterMediaTypeforIncompleteTimeout(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw' & SRGS Xml MediaType
        Expect:
        1) [Test case] NRC recognize return should be successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) for event SWIrcst, value of Token GRMT should be application/x-swi-parameter
        """ 
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "945015260.ulaw"
        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar.grxml"
        test_media_type = 'xswiparameter'      
        test_grammar_uri = client.test_res_url + test_grammar     
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>9405<\/instance.+\/interpretation.+\/result>"
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_event_to_checklist(event="EVNT", value="SWIgrld")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:           
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            #msg = "Test recognition result 1: \n" + test_result + "\n"
            #self.debug(msg)
            #print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()
            kafka.cleanup()

    def test0052_UriGrammarXswiparameterMediaTypeforIncompleteTimeout_1(self):
       
        client = gRPCClient()
  
        test_audio = "945015260.ulaw"
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        test_grammar_type2 = 'uri_grammar'
        test_grammar = "parameter_grammar.grxml"
        test_media_type = 'xswiparameter'      
        test_grammar_uri = client.test_res_url + test_grammar     
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
                   
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>9405<\/instance.+\/interpretation.+\/result>" 
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        
        try:
                   
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()


    def test0053_UriGrammarXswiparameterMediaTypefornBest3(self):
      
        client = gRPCClient()
        
        test_audio = 'voicenospeech_short.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_nBest3.grxml"
        test_media_type = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri = client.test_res_url + test_grammar     
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2) 
        test_recogRes = [test_recogRes1, test_recogRes2]
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)
        test_expect = "<?xml.+<result><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation></result>"
          
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)       
        
        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            #msg += "Test recognition result 2: \n" + test_result + "\n"
            #self.debug(msg)
            #print(msg)  # for debug
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()


    def test054_ClientDataMapWithSingleEventSingleToken(self):

        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_yes.grxml"
        test_media_type = 'srgsxml'    
        test_grammar_uri = client.test_res_url + test_grammar
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,mediaType=test_media_type)
        testClientData= {
        }
         #update testClientData dictionary with event and key value pair
        testClientData["NUANqatestevent1"] = "key11=value11";   
        test_recInit = client.recognition_init(test_recogParams, test_recogRes, clientData=testClientData)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test055_ClientDataMapWithSingleEventMultipleToken(self):

        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_yes.grxml"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
       
        #define the empty dictionary
        testClientData= {
        }
        #update testClientData dictionary with event and key value pair
        testClientData["NUANqatestevent1"] = "key11=value11|key12=value12";     
        test_recInit = client.recognition_init(test_recogParams, test_recogRes, clientData=testClientData)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test056_ClientDataMapWithMultipleEventMultipleToken(self):

        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_yes.grxml"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,mediaType=test_media_type)
        #define the empty dictionary
        testClientData= {
        }
        #update testClientData dictionary with event and key value pair
        testClientData["NUANqatestevent1"] = "key11=value11|key12=value12";  
        testClientData["NUANqatestevent2"] = "key21=value11|key22=value12";
        testClientData["NUANqatestevent3"] = "key31=value11|key32=value12";  
        test_recInit = client.recognition_init(test_recogParams, test_recogRes, clientData=testClientData)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test057_SessionID(self):

        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_yes.grxml"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar  
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>" 
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)      
        #define the empty dictionary
        testClientData= {
        }
        testClientData["SWIapps"] = "SESN=0a031728_00001170_487cd166_3a3f_0003|STEP=3"    
        test_recInit = client.recognition_init(test_recogParams, test_recogRes, clientData=testClientData)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0058_BuiltinGrammarZipCode(self):
        """
        Test NRC recognition Builtin alphanum grammar with audio 'alphanum_m385m5.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) value of Token URI should be builtin:grammar/zipcode
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "zip_43405.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'zipcode'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/zipcode.+<instance>43405<\/instance.+\/interpretation.+\/result>"
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/zipcode")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/zipcode")
        
        
        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()
            
    def test0059_BuiltinGrammarCreditCard(self):
        """
        Test NRC recognition Builtin alphanum grammar with audio 'alphanum_m385m5.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) value of Token URI should be builtin:grammar/creditcard
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "creditCard_4125169977837959.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'creditcard'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/creditcard.+<instance>4125169977837959<\/instance.+\/interpretation.+\/result>"
        test_expect_callLog = "<result><interpretation grammar=.+builtin:grammar\/creditcard.+<instance>FluentD redacted possible CCN<\/instance.+\/interpretation.+\/result>"
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect_callLog)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect_callLog)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/creditcard")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/creditcard")
  
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0060_BuiltinGrammarAplphanum_lc(self):
        """
        Test NRC recognition Builtin alphanum grammar with audio 'alphanum_m385m5.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) value of Token URI should be builtin:grammar/alphanum_lc
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "alphanum_lc.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'alphanum_lc'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/alphanum_lc.+<instance>m385m5<\/instance.+\/interpretation.+\/result>"
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/alphanum_lc")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/alphanum_lc")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0061_BuiltinGrammarPostcode(self):
        """
        Test NRC recognition Builtin alphanum grammar with audio 'alphanum_m385m5.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) value of Token URI should be builtin:grammar/postcode
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "zip_43405.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'postcode'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/postcode.+<instance>43405<\/instance.+\/interpretation.+\/result>"
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/postcode")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/postcode")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0062_BuiltinGrammarCCexpDate(self):
        """
        Test NRC recognition Builtin alphanum grammar with audio 'alphanum_m385m5.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) value of Token URI should be builtin:grammar/ccexpdate
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "ccexpDate_20230228.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'ccexpdate'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/ccexpdate.+<instance>20300228<\/instance.+\/interpretation.+\/result>"
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/ccexpdate")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/ccexpdate")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0063_BuiltinGrammarSocialSecurity(self):
        """
        Test NRC recognition Builtin alphanum grammar with audio 'alphanum_m385m5.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) value of Token URI should be builtin:grammar/socialsecurity
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "ss_601061777.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'socialsecurity'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/socialsecurity.+<instance>601061777<\/instance.+\/interpretation.+\/result>"
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/socialsecurity")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/socialsecurity")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0064_BuiltinGrammarHelp(self):
        """
        Test NRC recognition Builtin alphanum grammar with audio 'alphanum_m385m5.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) value of Token URI should be builtin:grammar/help
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "Help.alaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'help'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/help.+<instance>help<\/instance.+\/interpretation.+\/result>"
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/help")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/help")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,recInit=test_recInit)
            time.sleep(3)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0065_BuiltinGrammarExit(self):
        """
        Test NRC recognition Builtin alphanum grammar with audio 'alphanum_m385m5.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) value of Token URI should be builtin:grammar/exit
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "Exit.alaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'exit'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/exit.+<instance>exit<\/instance.+\/interpretation.+\/result>"
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/exit")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/exit")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()
            
    def test0066_BuiltinGrammarOperator(self):
        """
        Test NRC recognition Builtin alphanum grammar with audio 'alphanum_m385m5.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) value of Token URI should be builtin:grammar/operator
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "Operator.alaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'operator'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/operator.+<instance>operator<\/instance.+\/interpretation.+\/result>"
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/operator")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/operator")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()
                 
            
    def test0067_SessionTimeout(self):
        """
        Test NRC recognition Builtin grammar with SessionTimeout.alaw
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation validation] verify NRC call log & utterance from this case via QA NRC automated call logging test
            a) Grammar related events all presented in the call log, including: SWIgrld, SWIldst, SWIldnd;
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = "SessionTimeout.alaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_expect1 = "code: 418"                  # code 1
        test_expect2 = 'message: \"Session Timeout' # message None
        expectResult = ""
        #         
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect2)
        test_record_1.set_checklist_types(["Basic"]) 
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
           

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()
            
            
    def test0068_InactiveTimeout(self):

        client = gRPCClient()

        test_audio = "silence.ulaw"
        test_recInit = client.recognition_init()
        test_expect1 = "code: 404"
        test_expect2 = 'message: \"No Speech\"'
        test_expect3 = 'details: \"No speech detected\"'
        
        expectResult =""

        try:

            #test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            

    def test0069_UriGrammarXswiparameterMediaTypeforMaxSpeechTimeout(self):
      
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'
        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_maxspeechtimeout.grxml"
        test_media_type = 'xswiparameter'      
        test_grammar_uri = client.test_res_url + test_grammar        
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'        
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>" 
              
        try:
            
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test recognition result 1: \n" + test_result1 + "\n"        
            self.debug(msg)       
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            
            
    def test0070_UriGrammarXswiparameterMediaTypeforCompleteTimeout(self):
      
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_completetimeout.grxml"
        test_media_type = 'xswiparameter'              
        test_grammar_uri = client.test_res_url + test_grammar        
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'        
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)        
        test_recogRes = [test_recogRes1, test_recogRes2]      
        test_recogParams = client.recognition_swiparameters()       
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>9<\/instance.+\/interpretation.+\/result>"    
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
              
        try:
            
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            
    
    def test0071_UriGrammarXswiparameterMediaTypeforsensitivity(self):
        """
        Test NRC recognition Builtin digits grammar and xswi parameter grammar with audio '945015260_high2.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) value of Token URI in SWIgrld should be builtin:grammar/digits
            c) for event SWIrcst, value of Token GRMT should be application/x-swi-parameter
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = '945015260_high2.ulaw'
        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_sensitivity.grxml"
        test_media_type = 'xswiparameter'             
        test_grammar_uri = client.test_res_url + test_grammar             
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'  
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]       
        test_recogParams = client.recognition_swiparameters()       
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"            
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:    
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()
            
    def test0072_UriGrammarXswiparameterMediaTypefornBest0(self):
        """
        Test NRC recognition Builtin digits grammar and xswi parameter grammar with audio 'voicenospeech_short.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) value of Token URI in SWIgrld should be builtin:grammar/digits
            c) for event SWIrcst, value of Token GRMT should be application/x-swi-parameter
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'voicenospeech_short.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_nBest0.grxml"
        test_media_type = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri = client.test_res_url + test_grammar             
        
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'       
        
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]        
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)
        test_expect = "<?xml.+<result><interpretation><input><nomatch/></input><instance/></interpretation></result>"     
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        # test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="builtin:grammar\/digits")

        try:    
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0073_UriGrammarXswiparameterMediaTypefornBest1(self):
        """
        Test NRC recognition Builtin digits grammar and xswi parameter grammar with audio '945015260.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) value of Token URI in SWIgrld should be builtin:grammar/digits
            c) for event SWIrcst, value of Token GRMT should be application/x-swi-parameter
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = '945015260.ulaw'
        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_nBest1.grxml"
        test_media_type = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri = client.test_res_url + test_grammar     

        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'    
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)        
        test_recogRes = [test_recogRes1, test_recogRes2]        
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)
        test_expect = "<?xml.+<result><interpretation.+confidence=.+<instance.+/instance></interpretation></result>"       
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0074_UriGrammarXswiparameterMediaTypefornBest2(self):
        """
        Test NRC recognition Builtin digits grammar and xswi parameter grammar with audio 'voicenospeech_short.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) value of Token URI in SWIgrld should be builtin:grammar/digits
            c) for event SWIrcst, value of Token GRMT should be application/x-swi-parameter
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = 'voicenospeech_short.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_nBest2.grxml"
        test_media_type = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri = client.test_res_url + test_grammar     

        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'   
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)       
        test_recogRes = [test_recogRes1, test_recogRes2]       
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)
        test_expect = "<?xml.+<result><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation></result>"  
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()
            kafka.cleanup()
            
    def test0075_UriGrammarXswiparameterMediaTypefornBest4(self):
      
        client = gRPCClient()
        
        test_audio = 'voicenospeech_short.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_nBest4.grxml"
        test_media_type = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)

        test_expect = "<?xml.+<result><interpretation.+confidence=.+<instance.+/instance>.*</interpretation></result>"
        #test_expect = "<?xml.+<result><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation></result>"
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
                  
        try:
            
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)

            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            
    def test0076_UriGrammarXswiparameterMediaTypefornBest5(self):
      
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_nBest5.grxml"
        test_media_type = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)

        test_expect = "<?xml.+<result><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation><interpretation.+confidence=.+<instance.+/instance></interpretation></result>"
        
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
                  
        try:
            
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)

            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            
            
    def test0077_UriGrammarXswiparameter_swirec_extra_nbest_keys_SWI_spoken(self):
        """
        Test NRC recognition uri grammar yes and xswi parameter grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) Check Token URI in SWIgrld should be grammar uri
            c) For event SWIrcst, value of Token GRMT should be application/x-swi-parameter
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_extra_nbest_keys_SWI_spoken.grxml"
        test_media_type = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "uri_grammar_yes.grxml"
        test_media_type2 = 'srgsxml'      
        test_grammar_uri2 = client.test_res_url + test_grammar2 
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        
        test_recogRes = [test_recogRes1, test_recogRes2]
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_spoken>yes</SWI_spoken></instance></interpretation></result>"
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri2)
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri2)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0078_UriGrammarXswiparameter_swirec_extra_nbest_keys_SWI_utteranceSNR(self):
        """
        Test NRC recognition uri grammar yes and xswi parameter grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) Check Token URI in SWIgrld should be grammar uri
            c) For event SWIrcst, value of Token GRMT should be application/x-swi-parameter
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_extra_nbest_keys_SWI_utteranceSNR.grxml"
        test_media_type = 'xswiparameter'
        test_confLevel = 0
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "uri_grammar_yes.grxml"
        test_media_type2 = 'srgsxml'      
        test_grammar_uri2 = client.test_res_url + test_grammar2 
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)

        test_recogRes = [test_recogRes1, test_recogRes2]
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_utteranceSNR>25.000000</SWI_utteranceSNR></instance></interpretation></result>"
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri2)
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri2)
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0079_UriGrammarXswiparameter_swirec_extra_nbest_keys_SWI_literalConfidence(self):
        """
        Test NRC recognition uri grammar yes and xswi parameter grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) Check Token URI in SWIgrld should be grammar uri
            c) For event SWIrcst, value of Token GRMT should be application/x-swi-parameter
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_extra_nbest_keys_SWI_literalConfidence.grxml"
        test_media_type = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "uri_grammar_yes.grxml"
        test_media_type2 = 'srgsxml'      
        test_grammar_uri2 = client.test_res_url + test_grammar2 

        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        #test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)
        test_recogRes = [test_recogRes1, test_recogRes2]        
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literalConfidence>756.658203125</SWI_literalConfidence></instance></interpretation></result>"
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri2)
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri2)

        try:    
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0080_UriGrammarXswiparameter_swirec_extra_nbest_keys_SWI_disallow(self):
      
        client = gRPCClient()
        
        test_audio = 'yes.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_extra_nbest_keys_SWI_disallow.grxml"
        test_media_type = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "uri_grammar_yes.grxml"
        test_media_type2 = 'srgsxml'      
        test_grammar_uri2 = client.test_res_url + test_grammar2 
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        #test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)
        
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)

        test_expect = "<?xml.+<result><interpretation grammar=.*<instance></instance></interpretation></result>"
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
                  
        try:
            
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)

            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            
    def test0081_UriGrammarXswiparameter_swirec_extra_nbest_keys_SWI_literalTimings(self):
        """
        Test NRC recognition uri grammar yes and xswi parameter grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) Check Token URI in SWIgrld should be grammar uri
            c) For event SWIrcst, value of Token GRMT should be application/x-swi-parameter
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_extra_nbest_keys_SWI_literalTimings.grxml"
        test_media_type = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "uri_grammar_yes.grxml"
        test_media_type2 = 'srgsxml'      
        test_grammar_uri2 = client.test_res_url + test_grammar2 
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        #test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)
        
        test_recogRes = [test_recogRes1, test_recogRes2]
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)
        test_expect = "<?xml.+<result><interpretation grammar=.+confidence=.+<instance><SWI_literalTimings><alignment type=\"word\" unit_msecs=\"1\"><word start=\"720\" end=\"1150\" confidence=\"0.00\">yes</word></alignment></SWI_literalTimings></instance></interpretation></result>"
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri2)
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri2)

        try:    
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()
            kafka.cleanup()

    def test0082_UriGrammarXswiparameter_swirec_extra_nbest_keys_SWI_attributes(self):
        """
        Test NRC recognition uri grammar yes and xswi parameter grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) Check Token URI in SWIgrld should be grammar uri
            c) For event SWIrcst, value of Token GRMT should be application/x-swi-parameter
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_extra_nbest_keys_SWI_attributes.grxml"
        test_media_type = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "uri_grammar_yes.grxml"
        test_media_type2 = 'srgsxml'      
        test_grammar_uri2 = client.test_res_url + test_grammar2 
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        
        test_recogRes = [test_recogRes1, test_recogRes2]
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)
        test_expect = "<?xml.+<result><interpretation grammar=.+confidence=.+<instance><SWI_attributes></SWI_attributes></instance></interpretation></result>"
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri2)
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri2)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0083_UriGrammarXswiparameter_swirec_extra_nbest_keys_SWI_rawScore(self):
        """
        Test NRC recognition uri grammar yes and xswi parameter grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) Check Token URI in SWIgrld should be grammar uri
            c) For event SWIrcst, value of Token GRMT should be application/x-swi-parameter
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_extra_nbest_keys_SWI_rawScore.grxml"
        test_media_type = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "uri_grammar_yes.grxml"
        test_media_type2 = 'srgsxml'      
        test_grammar_uri2 = client.test_res_url + test_grammar2 
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        
        test_recogRes = [test_recogRes1, test_recogRes2]
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)
        test_expect = "<?xml.+<result><interpretation grammar=.+confidence=.+<instance><SWI_rawScore>-1020.016418</SWI_rawScore></instance></interpretation></result>"
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri2)
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri2)

        try:    
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0084_UriGrammarXswiparameter_swirec_extra_nbest_keys_SWI_confidence(self):
        """
        Test NRC recognition uri grammar yes and xswi parameter grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) Check Token URI in SWIgrld should be grammar uri
            c) For event SWIrcst, value of Token GRMT should be application/x-swi-parameter
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_extra_nbest_keys_SWI_confidence.grxml"
        test_media_type = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "uri_grammar_yes.grxml"
        test_media_type2 = 'srgsxml'      
        test_grammar_uri2 = client.test_res_url + test_grammar2 
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        
        test_recogRes = [test_recogRes1, test_recogRes2]
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_confidence>0</SWI_confidence></instance></interpretation></result>"
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri2)
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri2)
        
        try:
            
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()
            kafka.cleanup()

    def test0085_UriGrammarXswiparameter_swirec_extra_nbest_keys_SWI_bestModel(self):
      
        client = gRPCClient()
        
        test_audio = 'yes.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_extra_nbest_keys_SWI_bestModel.grxml"
        test_media_type = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "uri_grammar_yes.grxml"
        test_media_type2 = 'srgsxml'      
        test_grammar_uri2 = client.test_res_url + test_grammar2 
       
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)
        
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)

        test_expect = "<?xml.+<result><interpretation grammar=.+confidence=.+<instance><SWI_bestModel>/usr/local/Nuance/nrc/nrlang/en.us/10.0.2/models/FirstPass/models.hmm</SWI_bestModel></instance></interpretation></result>"
        
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
                  
        try:
            
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)

            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            
            
    def test0086_UriGrammarXswiparameter_swirec_barge_in_mode_normal(self):
        """
        Test NRC recognition uri grammar yes and xswi parameter grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) Check Token URI in SWIgrld should be grammar uri
            c) For event SWIrcst, value of Token GRMT should be application/x-swi-parameter
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_barge_in_mode_normal.grxml"
        test_media_type = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "uri_grammar_yes.grxml"
        test_media_type2 = 'srgsxml'      
        test_grammar_uri2 = client.test_res_url + test_grammar2 
        
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)
        test_expect = "<?xml.+<result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal><SWI_grammarName>" + client.test_res_url + "uri_grammar_yes.grxml</SWI_grammarName><SWI_meaning>{SWI_literal:yes}</SWI_meaning></instance></interpretation></result>"
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri2)
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri2)

        try:   
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(3)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0087_UriGrammarXswiparameter_swirec_app_state_tokens(self):
        """
        Test NRC recognition uri grammar yes and xswi parameter grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) Check Token URI in SWIgrld should be grammar uri
            c) For event SWIrcst, value of Token GRMT should be application/x-swi-parameter
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_app_state_tokens.grxml"
        test_media_type = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "uri_grammar_yes.grxml"
        test_media_type2 = 'srgsxml'      
        test_grammar_uri2 = client.test_res_url + test_grammar2 
        
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)
        
        test_recogRes = [test_recogRes1, test_recogRes2]
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)
        test_expect = "<?xml.+<result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal><SWI_grammarName>" + client.test_res_url + "uri_grammar_yes.grxml</SWI_grammarName><SWI_meaning>{SWI_literal:yes}</SWI_meaning></instance></interpretation></result>"
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri2)
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri2)

        try:    
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()
            kafka.cleanup()

    def test0088_UriGrammarXswiparameter_swirec_extra_nbest_keys_SWI_utteranceSNR_Inline(self):
        """
        Test NRC recognition inline grammar and xswi parameter grammar with audio 'one.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) Check Token URI in SWIgrld should be grammar uri
            c) For event SWIrcst, value of Token GRMT should be application/x-swi-parameter
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'one.ulaw'
        
        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_extra_nbest_keys_SWI_utteranceSNR.grxml"
        test_media_type = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar2 = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_one\"> <rule id=\"yes_one\" scope=\"public\">\n<one-of>\n<item>one</item>\n<item>yes</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type2 = 'inline_grammar'
        test_media_type2 = 'srgsxml'
        #test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>one</SWI_literal>.+<SWI_meaning.+one.+SWI_meaning></instance></interpretation></result>"

        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar2, mediaType=test_media_type2)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes = [test_recogRes1, test_recogRes2]
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)
        test_expect = "<?xml.+<result><interpretation grammar=\"2760195588039232203\" confidence=\"94\"><input mode=\"speech\">one</input><instance><SWI_utteranceSNR>82.000000</SWI_utteranceSNR></instance></interpretation></result>"
        test_expect_callLog = "<?xml.+<result><interpretation grammar=\"FluentD redacted possible CCN\" confidence=\"94\"><input mode=\"speech\">one</input><instance><SWI_utteranceSNR>82.000000</SWI_utteranceSNR></instance></interpretation></result>"
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect_callLog)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect_callLog)
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=en-US")
        
        try:    
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(3)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()
            kafka.cleanup()

    def test0300_BuiltinGrammarInvalidWeightZero(self):
        """
        Negative testcase: Test NRC bultin grammar weight = 0.
        Valid range 1-32767
        Expected Result:
            message: "Bad Request"
			details: "Grammar weight is out of range. Valid range is [1,32767]."
        """
        client = gRPCClient()

        test_audio = "1.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_grammar_weight = 0

        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Grammar weight is out of range."

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data,
                                                    grammarWeight=test_grammar_weight)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0301_InlineGrammarInvalidWeightZero(self):
        """
        Negative testcase: Test NRC inline grammar weight = 0.
        Valid range 1-32767
        Expected Result:
            message: "Bad Request"
            details: "Grammar weight is out of range. Valid range is [1,32767]."
        """
        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar_type = 'inline_grammar'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type = 'srgsxml'

        test_grammar_weight = 0

        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Grammar weight is out of range."

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, grammarWeight=test_grammar_weight)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0302_UriGrammarInvalidWeightZero(self):
        """
        Negative testcase: Test NRC URI grammar weight = 0.
        Valid range 1-32767
        Expected Result:
            message: "Bad Request"
            details: "Grammar weight is out of range. Valid range is [1,32767]."
        """
        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_yes.grxml"

        test_media_type = 'srgsxml'

        test_grammar_uri = client.test_res_url + test_grammar
        test_grammar_weight = 0

        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Grammar weight is out of range."

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type, grammarWeight=test_grammar_weight)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

            # ------------------URI Parameter---------------------------------------------------------

    def test0303_BuiltinGrammarInvalidWeightNegativeValue(self):
        """
        Negative testcase: Test NRC bultin grammar weight = -1.
        Valid range 1-32767
        Expected Result:
            message: "Bad Request"
            details: "Grammar weight is out of range. Valid range is [1,32767]."
        """
        client = gRPCClient()

        test_audio = "1.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_grammar_weight = -1

        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Grammar weight is out of range."

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data,
                                                    grammarWeight=test_grammar_weight)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0304_InlineGrammarInvalidWeightNegativeValue(self):
        """
        Negative testcase: Test NRC inline grammar weight = -1.
        Valid range 1-32767
        Expected Result:
            message: "Bad Request"
            details: "Grammar weight is out of range. Valid range is [1,32767]."
        """
        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar_type = 'inline_grammar'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_media_type = 'srgsxml'

        test_grammar_weight = -1

        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Grammar weight is out of range."

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, grammarWeight=test_grammar_weight)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0305_UriGrammarInvalidWeightNegativeValue(self):
        """
        Negative testcase: Test NRC URI grammar weight = -1.
        Valid range 1-32767
        Expected Result:
            message: "Bad Request"
            details: "Grammar weight is out of range. Valid range is [1,32767]."
        """
        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_yes.grxml"

        test_media_type = 'srgsxml'

        test_grammar_uri = client.test_res_url + test_grammar
        test_grammar_weight = -1

        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Grammar weight is out of range."

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type, grammarWeight=test_grammar_weight)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0306_UriGrammarParametersInvalidContentBase2(self):
        """
        Negative testcase: Test NRC missing content base.
        Expected Result:
            message: "Bad Request"
            details: "Failed to load RecognitionResource"
        """
        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_yes.grxml"
        test_media_type = 'srgsxml'
        # invalid base uri(grammar is not present)
        test_contentBase = 'missing.file'
        # test_grammar_uri = client.test_res_url + test_grammar
        test_grammar_uri = test_grammar

        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource "

        test_UriParams = client.recognition_UriGrammarParam(contentBase=test_contentBase)
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type, uriParameters=test_UriParams)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            time.sleep(20)
            

#*************************************************************************************************************************************************************************

    def test0089_UriGrammarXswiparameterMediaTypeforCompleteTimeout_default(self):
      
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_completetimeout_default.grxml"
        test_media_type = 'xswiparameter'      
        
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
       
        test_expect = "<result><interpretation grammar=.+confidence=.+<instance>945015260</instance>.*</instance></interpretation></result>"    
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
              
        try:
            
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            #print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test0090_UriGrammarXswiparameterMediaTypeforCompleteTimeout_Invalid(self):
      
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_completetimeout_Invalid.grxml"
        test_media_type = 'xswiparameter'      
        
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource at index"

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)

    def test0091_UriGrammarXswiparameterMediaTypeforIncompleteTimeout_default(self):
       
        client = gRPCClient()
  
        test_audio = "945015260.ulaw"
        test_grammar_type1 = 'builtin'
        test_grammar_data1 = 'digits'
        
        #loaded swi parameter grammar parameter_grammar.grxml to set value of incompletetimeout value as 10
        test_grammar_type2 = 'uri_grammar'
        test_grammar = "parameter_grammar_incompleteTimeout_default.grxml"
        test_media_type = 'xswiparameter'      
        test_grammar_uri = client.test_res_url + test_grammar     

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
                   
        test_expect = "<result><interpretation grammar=.+confidence=.+<instance>945015260</instance>.*</instance></interpretation></result>"
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        
        try:
                   
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            
    def test0092_UriGrammarXswiparameterMediaTypeforInCompleteTimeout_Invalid(self):
      
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_IncompleteTimeout_Invalid.grxml"
        test_media_type = 'xswiparameter'      
        
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource at index"

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)
            
    #Sensitivity of the speech detector when looking for speech Value Float: 0.0-1.0
    def test0093_UriGrammarXswiparameterSensitivity_Invalid_High(self):
      
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_sensitivity_Invalid_high.grxml"
        test_media_type = 'xswiparameter'      
        
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource at index"

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)
            
    #Sensitivity of the speech detector when looking for speech Value Float: 0.0-1.0.
    def test0094_UriGrammarXswiparameterSensitivity_Invalid_low(self):
      
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_sensitivity_Invalid_low.grxml"
        test_media_type = 'xswiparameter'      
        
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource at index"

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)
            
    def test0095_UriGrammarXswiparameterNbest_Invalid_low(self):
      
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_nBest_invalid_low.grxml"
        test_media_type = 'xswiparameter'      
        
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource at index"

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)
            
    def test0096_UriGrammarXswiparameterNbest_Invalid_high(self):
      
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_nBest_invalid_high.grxml"
        test_media_type = 'xswiparameter'      
        
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource at index"

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)

    
    #Confidence threshold for magic word recognition results Value range 0-999 Default-500    
    def test0097_UriGrammarXswiparamete_swirec_magic_word_conf_thresh_default(self):
        """
        Test NRC recognition builtin digits grammar and xswi parameter grammar with audio '945015260.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) Check Token URI in SWIgrld should be grammar uri and "builtin:grammar/digits"
            c) For event SWIrcst, value of Token GRMT should be application/x-swi-parameter
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_magic_word_conf_thresh_default.grxml"
        test_media_type = 'xswiparameter'      
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        test_expect1 = "<result><interpretation grammar=.+confidence=.+<instance>945015260</instance>.*</instance></interpretation></result>"
        
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect1)
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0098_UriGrammarXswiparameter_swirec_magic_word_conf_thresh_Invalid_high(self):
      
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_magic_word_conf_thresh_invalid_high.grxml"
        test_media_type = 'xswiparameter'      
        
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource at index"

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)

            
    def test0099_UriGrammarXswiparameter_swirec_magic_word_conf_thresh_Invalid_low(self):
      
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_magic_word_conf_thresh_invalid_low.grxml"
        test_media_type = 'xswiparameter'      
        
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource at index"

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)

            
    #Confidence threshold for selective_barge_in mode. Value range 0-999 Default-500    
    def test00100_UriGrammarXswiparamete_swirec_selective_barge_in_conf_thresh_default(self):
        """
        Test NRC recognition builtin digits grammar and xswi parameter grammar with audio '945015260.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) Check Token URI in SWIgrld should be grammar uri and "builtin:grammar/digits"
            c) For event SWIrcst, value of Token GRMT should be application/x-swi-parameter
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_selective_barge_in_conf_thresh_default.grxml"
        test_media_type = 'xswiparameter'      
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        test_expect1 = "<result><interpretation grammar=.+confidence=.+<instance>945015260</instance>.*</instance></interpretation></result>"
        
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect1)
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test00101_UriGrammarXswiparameter_swirec_selective_barge_in_conf_thresh_Invalid_high(self):
      
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_selective_barge_in_conf_thresh_invalid_high.grxml"
        test_media_type = 'xswiparameter'      
        
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource at index"

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)
            
    def test00102_UriGrammarXswiparameter_swirec_selective_barge_in_conf_thresh_Invalid_low(self):
      
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_selective_barge_in_conf_thresh_invalid_low.grxml"
        test_media_type = 'xswiparameter'      
        
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource at index"

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)
            
    #Maximum number of parses evaluated by the recognizer for a single literal string. Value range 1-99 Default-10    
    def test00103_UriGrammarXswiparamete_swirec_max_parses_per_literal_default(self):
        """
        Test NRC recognition builtin digits grammar and xswi parameter grammar with audio '945015260.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) Check Token URI in SWIgrld should be grammar uri and "builtin:grammar/digits"
            c) For event SWIrcst, value of Token GRMT should be application/x-swi-parameter
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_max_parses_per_literal_default.grxml"
        test_media_type = 'xswiparameter'      
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        test_expect1 = "<result><interpretation grammar=.+confidence=.+<instance>945015260</instance>.*</instance></interpretation></result>"
        
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect1)
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test00104_UriGrammarXswiparameter_swirec_max_parses_per_literal_Invalid_low(self):
      
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_max_parses_per_literal_invalid_low.grxml"
        test_media_type = 'xswiparameter'      
        
        test_grammar_uri = client.test_res_url + test_grammar     
        
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource at index"

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)
            
    def test00105_UriGrammarXswiparameter_swirec_max_parses_per_literal_Invalid_high(self):
      
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_max_parses_per_literal_invalid_high.grxml"
        test_media_type = 'xswiparameter'       
        test_grammar_uri = client.test_res_url + test_grammar     
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource at index"

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)

    #swirec_max_sentences_tried -->Maximum number of candidates for filling the n-best list.. Value range 1-999999 Default-999999    
    def test00106_UriGrammarXswiparamete_swirec_max_sentences_tried_default(self):
        """
        Test NRC recognition builtin digits grammar and xswi parameter grammar with audio '945015260.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) Check Token URI in SWIgrld should be grammar uri and "builtin:grammar/digits"
            c) For event SWIrcst, value of Token GRMT should be application/x-swi-parameter
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_max_sentences_tried_default.grxml"
        test_media_type = 'xswiparameter'      
        test_grammar_uri = client.test_res_url + test_grammar

        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        test_expect1 = "<result><interpretation grammar=.+confidence=.+<instance>945015260</instance>.*</result>"
        
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect1)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect1)
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()
            
    def test00107_UriGrammarXswiparameter_swirec_max_sentences_tried_Invalid_low(self):
      
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_max_sentences_tried_Invalid_low.grxml"
        test_media_type = 'xswiparameter'      
        test_grammar_uri = client.test_res_url + test_grammar     
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource at index"

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)
            
#***************************************************************************************************************************************

    def test00108_UriGrammar_MovieScript_249(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        """
        client = gRPCClient()
        
        test_audio = 'movie.ulaw'
        test_grammar = "movies_script249.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance>The Good, the Bad and the Ugly<SWI_meaning>The Good, the Bad and the Ugly</SWI_meaning><SWI_literal>The Good, the Bad and the Ugly</SWI_literal><SWI_grammarName>" + client.test_res_url + "movies_script249.grxml</SWI_grammarName></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        
        try:
            
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)    
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00109_UriGrammar_MovieScript_250(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'movie.ulaw'
        test_grammar = "movies_script250.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance>The Good, the Bad and the Ugly<SWI_meaning>The Good, the Bad and the Ugly</SWI_meaning><SWI_literal>The Good, the Bad and the Ugly</SWI_literal><SWI_grammarName>" + client.test_res_url + "movies_script250.grxml</SWI_grammarName></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
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

    def test00110_UriGrammar_MovieScript_251(self):
        """
        Test NRC recognition URI grammar with audio 'movie.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        """
        client = gRPCClient()
        
        test_audio = 'movie.ulaw'
        test_grammar = "movies_script251.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
       
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance>The Good, the Bad and the Ugly<SWI_meaning>The Good, the Bad and the Ugly</SWI_meaning><SWI_literal>The Good, the Bad and the Ugly</SWI_literal><SWI_grammarName>" + client.test_res_url + "movies_script251.grxml</SWI_grammarName></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        time.sleep(15)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        time.sleep(15)
        try:
            
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)   
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
    def test00111_UriGrammar_big_script1817(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/srgs+xml
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = 'movie.ulaw'
        test_grammar = "big_script1817.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance>The Good, the Bad and the Ugly<SWI_meaning>The Good, the Bad and the Ugly</SWI_meaning><SWI_literal>The Good, the Bad and the Ugly</SWI_literal>.*</instance></interpretation></result>"
        
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        time.sleep(30)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        time.sleep(30)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/srgs+xml")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(30)
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
            
    def test00112_UriGrammar_big_script2600(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        """
        client = gRPCClient()
        
        test_audio = 'movie.ulaw'
        test_grammar = "big_script2600.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance>The Good, the Bad and the Ugly<SWI_meaning>The Good, the Bad and the Ugly</SWI_meaning><SWI_literal>The Good, the Bad and the Ugly</SWI_literal>.*</instance></interpretation></result>"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        
        try:
            
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)    
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
            
    def test00113_Tier4Grammar_Test1_GramSSM(self):
        """
        Test NRC recognition SSRM URI grammar with audio 'sleet_and_snow_ulaw_audio.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/x-swi-grammar
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = 'sleet_and_snow_ulaw_audio.ulaw'
        test_grammar = "Test1_GramSSM.gram"  
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'

        test_grammar_uri = client.test_res_url + test_grammar
        print("Test grammar URI: " + test_grammar_uri + "\n")
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><Test1_SSM confidence=\"100\">TOMORROW</Test1_SSM><SWI_literal>there will be sleet and snowy tomorrow</SWI_literal>.*<SWI_meaning>{Test1_SSM:TOMORROW}</SWI_meaning><SWI_ssmMeanings><Test1_SSM>TOMORROW</Test1_SSM></SWI_ssmMeanings><SWI_ssmConfidences><Test1_SSM>100</Test1_SSM></SWI_ssmConfidences></instance></interpretation></result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-grammar")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()
            
            
    def test00114_Tier4swiparameter_swirec_extra_nbest_keys_SWI_semanticSource(self):
        """
        Test NRC recognition SSRM URI grammar and parameter grammar with audio 'sleet_and_snow_ulaw_audio.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/x-swi-parameter
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = 'sleet_and_snow_ulaw_audio.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_extra_nbest_keys_SWI_semanticSource.grxml"
        test_media_type = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri = client.test_res_url + test_grammar   

        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "Test1_GramSSM.gram"
        #test_media_type2 = 'srgsxml'  
        test_media_type2 = 'xswigrammar'    
        test_grammar_uri2 = client.test_res_url + test_grammar2 

        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes = [test_recogRes1, test_recogRes2]
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)
        test_expect = "<?xml.+<result><interpretation grammar=.+confidence=.+</input><instance><Test1_SSM confidence=\"100\">TOMORROW</Test1_SSM><SWI_semanticSource><Test1_SSM>ssm</Test1_SSM></SWI_semanticSource><SWI_ssmMeanings><Test1_SSM>TOMORROW</Test1_SSM></SWI_ssmMeanings><SWI_ssmConfidences><Test1_SSM>100</Test1_SSM></SWI_ssmConfidences></instance></interpretation></result>"
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri2)
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri2)

        try:    
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test00115_Tier4Grammar_SLM_Yes(self):
        """
        Test Tier4 Statistical Language Model - SLM_Yes.gram
        Input audio sent - 'yes.ulaw
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/x-swi-grammar
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = 'yes.ulaw'
        test_grammar = "SLM_Yes.gram"
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'
        test_grammar_uri = client.test_res_url + test_grammar
        
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_meaning>Yes</SWI_meaning><SWI_literal>Yes</SWI_literal>.*</instance></interpretation></result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-grammar")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()
            
    def test00116_Tier4Grammar_SLM_snow(self):
        """
          Test Tier4 Statistical Language Model - SLM_snow.gram
          Input audio sent - 'sleet_and_snow_ulaw_audio.ulaw
          Expected Result: NRC recognize return should be successful
        """
        client = gRPCClient()
        
        test_audio = 'sleet_and_snow_ulaw_audio.ulaw'
        test_grammar = "SLM_snow.gram"     
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'
        test_grammar_uri = client.test_res_url + test_grammar

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_meaning>there will sleet snowy tomorrow</SWI_meaning><SWI_literal>there will sleet snowy tomorrow</SWI_literal>.*</instance></interpretation></result>"

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
    def test00117_Tier4Grammar_SLM_Movie_Training(self):
        """
          Test Tier4 Statistical Language Model - SLM_Movie_Training.gram
          Input audio sent - 'Movie1.ulaw
          Expected Result: NRC recognize return should be successful
        """
        client = gRPCClient()
        
        test_audio = 'Movie1.ulaw'
        test_grammar = "SLM_Movie_Training.gram" 
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'

        test_grammar_uri = client.test_res_url + test_grammar

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_meaning>i want to want to the movie</SWI_meaning><SWI_literal>i want to want to the movie</SWI_literal>.*</instance></interpretation></result>"

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
    def test00118_Tier4Grammar_RPTest1(self):
        """
        Test Tier4 Robust Parsing grammar - RPTest1.gram
        Input audio sent - see_film.ulaw
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/x-swi-grammar
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = 'see_film.ulaw'
        test_grammar = "RPTest1.gram"
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'
        test_grammar_uri = client.test_res_url + test_grammar

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<result><interpretation grammar=.+confidence=.+<instance><SWI_meaning>i would really want to go to see that film</SWI_meaning><SWI_literal>i would really want to go to see that film</SWI_literal>.*</instance></interpretation></result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-grammar")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()
            
    def test00119_Tier4Grammar_Test1_GramSSM_srgsxml_MediaType(self):
        """
        Test Tier4 Statistical Semantic Model - Test1_GramSSM.gram
        Input audio sent - sleet_and_snow_ulaw_audio.ulaw
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/x-swi-grammar
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = 'sleet_and_snow_ulaw_audio.ulaw'
        test_grammar = "Test1_GramSSM.gram"
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'

        test_grammar_uri = client.test_res_url + test_grammar
        print("Test grammar URI: " + test_grammar_uri + "\n")
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<result><interpretation grammar=.+confidence=.+<instance><Test1_SSM confidence=\"100\">TOMORROW</Test1_SSM><SWI_literal>there will be sleet and snowy tomorrow</SWI_literal>.*<SWI_meaning>{Test1_SSM:TOMORROW}</SWI_meaning><SWI_ssmMeanings><Test1_SSM>TOMORROW</Test1_SSM></SWI_ssmMeanings><SWI_ssmConfidences><Test1_SSM>100</Test1_SSM></SWI_ssmConfidences></instance></interpretation></result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-grammar")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri)
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()
                        
    def test00120_Tier4Grammar_SLM_Movie_Training_srgsxml_MediaType(self):
        """
        Test Tier4 Statistical Language Model - SLM_snow.gram
        Input audio sent - 'sleet_and_snow.alaw
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/x-swi-grammar
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = 'Movie1.ulaw'
        test_grammar = "SLM_Movie_Training.gram"    
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'
        test_grammar_uri = client.test_res_url + test_grammar

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<result><interpretation grammar=.+confidence=.+<instance><SWI_meaning>i want to want to the movie</SWI_meaning><SWI_literal>i want to want to the movie</SWI_literal>.*</instance></interpretation></result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-grammar")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test00121_Tier4Grammar_RPTest1_srgsxml_MediaType(self):
        """
        Test Tier4 Robust Parsing grammar - RPTest1.gram
        Input audio sent - 'see_film.ulaw
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/x-swi-grammar
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'see_film.ulaw'
        test_grammar = "RPTest1.gram"
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'
        test_grammar_uri = client.test_res_url + test_grammar

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "<result><interpretation grammar=.+confidence=.+<instance><SWI_meaning>i would really want to go to see that film</SWI_meaning><SWI_literal>i would really want to go to see that film</SWI_literal>.*</instance></interpretation></result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-grammar")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test00122_Tier4Grammar_Test1_GramSSM_noMatch(self):
        """
        Test Tier4 Statistical Semantic Model - Test1_GramSSM.gram
        Input audio sent - yes.ulaw
        Expect:
        1) [Test case] NRC recognize expected Result: SWIrec_STATUS_NO_MATCH
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/x-swi-grammar
            c) For event SWIrcnd, value of Token RENR should be prun
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = 'yes.ulaw'
        test_grammar = "Test1_GramSSM.gram"
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'
        test_grammar_uri = client.test_res_url + test_grammar

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, result_status="NO_MATCH")
        test_record_1.set_checklist_types(["Basic", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-grammar")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RENR", value="prun")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()
            
    def test00123_Tier4Grammar_SLM_Movie_Training_noMatch(self):
        """
        Test Tier4 Statistical Language Model - SLM_Movie_Training.gram
        Input audio sent - yes.ulaw
        Expect:
        1) [Test case] NRC recognize expected Result: SWIrec_STATUS_NO_MATCH
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/x-swi-grammar
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = 'yes.ulaw'
        test_grammar = "SLM_Movie_Training.gram"
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'
        test_grammar_uri = client.test_res_url + test_grammar

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, result_status="NO_MATCH")
        test_record_1.set_checklist_types(["Basic", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-grammar")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()
            
        
    def test00124_Tier4Grammar_RPTest1_noMatch(self):
        """
        Test Tier4 Robust parsing grammar - RPTest1.gram
        Input audio sent - yes.ulaw
        Expect:
        1) [Test case] NRC recognize expected Result: SWIrec_STATUS_NO_MATCH
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/x-swi-grammar
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'
        test_grammar = "SLM_Movie_Training.gram"
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'
        test_grammar_uri = client.test_res_url + test_grammar

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, result_status="NO_MATCH")
        test_record_1.set_checklist_types(["Basic", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-grammar")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test00125_Tier4Grammar_Test1_GramSSM_emma(self):
        """
        Test Tier4 Statistical Semantic Model - Test1_GramSSM.gram
        Input audio sent - sleet_and_snow_ulaw_audio.ulaw
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/x-swi-grammar
            c) For event SWIrslt, value of token MEDIA should be application/x-vnd.nuance.emma+xml
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'sleet_and_snow_ulaw_audio.ulaw'
        test_grammar = "Test1_GramSSM.gram"
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'
        test_result_format = 'emma'
        
        test_grammar_uri = client.test_res_url + test_grammar
        test_recogParams = client.recognition_parameters(resultFormat=test_result_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<?xml.+><emma:emma version=\"1.0\" xmlns:emma=.*<SWI_literal>there will be sleet and snowy tomorrow</SWI_literal><SWI_meaning>{Test1_SSM:TOMORROW}</SWI_meaning><SWI_ssmMeanings><Test1_SSM>TOMORROW</Test1_SSM></SWI_ssmMeanings><SWI_ssmConfidences><Test1_SSM>100</Test1_SSM></SWI_ssmConfidences></emma:interpretation></emma:emma>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-grammar")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="MEDIA", value="application/x-vnd.nuance.emma+xml")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test00126_Tier4Grammar_SLM_snow_emma(self):

        client = gRPCClient()
        
        test_audio = 'sleet_and_snow_ulaw_audio.ulaw'
        test_grammar = "SLM_snow.gram"
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'
        test_result_format = 'emma'
        test_grammar_uri = client.test_res_url + test_grammar
        time.sleep(30)
        test_recogParams = client.recognition_parameters(resultFormat=test_result_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<?xml.+><emma:emma version=\"1.0\" xmlns:emma=.*<SWI_meaning>there will sleet snowy tomorrow</SWI_meaning><SWI_literal>there will sleet snowy tomorrow</SWI_literal>.*</emma:emma>"

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()   

    def test00127_Tier4Grammar_RPTest1_emma(self):
        """
        Test Tier4 Robust Parsing grammar - RPTest1.gram
        Input audio sent - 'see_film.ulaw
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/x-swi-grammar
            c) For event SWIrslt, value of token MEDIA should be application/x-vnd.nuance.emma+xml
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'see_film.ulaw'
        test_grammar = "RPTest1.gram"
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'
        test_grammar_uri = client.test_res_url + test_grammar
        test_result_format = 'emma'
        test_recogParams = client.recognition_parameters(resultFormat=test_result_format)

        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<emma:emma version=\"1.0\" xmlns:emma=.*<SWI_meaning>i would really want to go to see that film</SWI_meaning><SWI_literal>i would really want to go to see that film</SWI_literal>.*</emma:emma>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-grammar")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="MEDIA", value="application/x-vnd.nuance.emma+xml")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_grammar_uri)
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test00128_Tier4Grammar_Test1_GramSSM_alaw(self):
        """
        Test Tier4 Statistical Semantic Model - Test1_GramSSM.gram
        Input audio sent - 'sleet_and_snow.alaw
        Expected Result: NRC recognize return should be successful
        """
        client = gRPCClient()
        
        test_audio = 'sleet_and_snow.alaw'
        test_grammar = "Test1_GramSSM.gram"
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'
        test_audio_format = 'alaw'      
        test_grammar_uri = client.test_res_url + test_grammar      
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)      
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><Test1_SSM confidence=\"100\">TOMORROW</Test1_SSM><SWI_literal>there will be sleet and snowy tomorrow</SWI_literal>.*<SWI_meaning>{Test1_SSM:TOMORROW}</SWI_meaning><SWI_ssmMeanings><Test1_SSM>TOMORROW</Test1_SSM></SWI_ssmMeanings><SWI_ssmConfidences><Test1_SSM>100</Test1_SSM></SWI_ssmConfidences></instance></interpretation></result>"
        

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
    def test00129_Tier4Grammar_SLM_snow_alaw(self):
        """
          Test Tier4 Statistical language Model - SLM_snow.gram
          Input audio sent - 'sleet_and_snow.alaw
          Expected Result: NRC recognize return should be successful
        """
        client = gRPCClient()
        
        test_audio = 'sleet_and_snow.alaw'
        test_grammar = "SLM_snow.gram"
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'
        test_audio_format = 'alaw'
        test_grammar_uri = client.test_res_url + test_grammar
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_meaning>there will sleet snowy tomorrow</SWI_meaning><SWI_literal>there will sleet snowy tomorrow</SWI_literal>.*</instance></interpretation></result>"
        
        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
            
    def test00130_Tier4Grammar_RPTest1_alaw(self):
        """
          Test Tier4 Robust parsing grammar - RPTest1.gram
          Input audio sent - see_film.alaw
          Expected Result: NRC recognize return should be successful
        """
        client = gRPCClient()
        
        test_audio = 'see_film.alaw'
        test_grammar = "RPTest1.gram"
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'
        test_audio_format = 'alaw'        
        test_grammar_uri = client.test_res_url + test_grammar       
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<result><interpretation grammar=.+confidence=.+<instance><SWI_meaning>i would really want to go to see that film</SWI_meaning><SWI_literal>i would really want to go to see that film</SWI_literal>.*</instance></interpretation></result>"
        

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
                   
    def test00131_Tier4GrammarSSM_InvalidMediaType(self):
        """
          Test Tier4 statistical semantic models - Test1_GramSSM.gram
          Input audio sent - sleet_and_snow.ulaw with Invalid media type
          Expected Result: NRC recognize return should not be successful with return code as 400
        """

        client = gRPCClient()

        test_audio = 'sleet_and_snow.ulaw'
        test_grammar = "Test1_GramSSM.gram"
        test_grammar_type = "uri_grammar"
        test_media_type = 'Invalid'
        test_expect4 = 'unknown enum label \"Invalid\"'
        test_grammar_uri = client.test_res_url + test_grammar
   
        try:
            test_recogParams = client.recognition_parameters()
            test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type)

        except (AssertionError, TimeoutException, Exception) as e:
            msg = "\nFound exception!\n" + str(e)
            # print(msg)
            if self.assertRecognitionResult(inputToCheck=str(e), expectResult=test_expect4):
                msg = "Test passed. Expected: \n" + msg + "\n"
                print(msg)
            else:
                self.fail(e)
                

    def test00132_Tier4GrammarSLM_InvalidMediaType(self):
        """
          Test Tier4 Semantic Language Model- SLM_snow.gram
          Input audio sent - see_film.alaw with Invalid media type
          Expected Result: NRC recognize return should not be successful with return code as 400
        """

        client = gRPCClient()

        test_audio = 'sleet_and_snow_ulaw_audio.ulaw'
        test_grammar = "SLM_snow.gram"
        test_grammar_type = "uri_grammar"
        test_media_type = 'Invalid'
        test_expect4 = 'unknown enum label \"Invalid\"'
        test_grammar_uri = client.test_res_url + test_grammar
   
        try:
            test_recogParams = client.recognition_parameters()
            test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type)

        except (AssertionError, TimeoutException, Exception) as e:
            msg = "\nFound exception!\n" + str(e)
            # print(msg)
            if self.assertRecognitionResult(inputToCheck=str(e), expectResult=test_expect4):
                msg = "Test passed. Expected: \n" + msg + "\n"
                print(msg)
            else:
                self.fail(e)
                
                
    def test00133_Tier4GrammarRP_InvalidMediaType(self):
        """
          Test Tier4 robust parsing grammar RPTest1.gram
          Input audio sent - see_film.alaw with Invalid media type
          Expected Result: NRC recognize return should not be successful with return code as 400
        """

        client = gRPCClient()

        test_audio = 'see_film.alaw'
        test_grammar = "RPTest1.gram"
        test_grammar_type = "uri_grammar"
        test_media_type = 'Invalid'
        test_expect4 = 'unknown enum label \"Invalid\"'
        test_grammar_uri = client.test_res_url + test_grammar
   
        try:
            test_recogParams = client.recognition_parameters()
            test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type)

        except (AssertionError, TimeoutException, Exception) as e:
            msg = "\nFound exception!\n" + str(e)
            # print(msg)
            if self.assertRecognitionResult(inputToCheck=str(e), expectResult=test_expect4):
                msg = "Test passed. Expected: \n" + msg + "\n"
                print(msg)
            else:
                self.fail(e)
                

    def test00134_Tier4GrammarFedex_emma_resultFormat_xswigrammar_mediaType(self):
        """
        Test Tier4 fedex grammar pr2000_SpeakFreelyMainMenu_DM.gram
        Input audio sent - ground_pickup.ulaw
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/x-swi-grammar
            c) For event SWIrslt, value of token MEDIA should be application/x-vnd.nuance.emma+xml
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = 'ground_pickup.ulaw'
        test_grammar = "pr2000_SpeakFreelyMainMenu_DM.gram"      
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'
        test_grammar_uri = client.test_res_url + test_grammar
        test_result_format = 'emma'
        test_recogParams = client.recognition_parameters(resultFormat=test_result_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<emma:emma version=\"1.0\" xmlns:emma=.*emma:tokens=\"scheduling ground pickup\">.*</emma:emma>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-grammar")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="MEDIA", value="application/x-vnd.nuance.emma+xml")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test00135_Tier4GrammarFedex_default_resultFormat_xswigrammar_mediaType(self):
        """
        Test Tier4 fedex grammar pr2000_SpeakFreelyMainMenu_DM.gram
        Input audio sent - ground_pickup.ulaw
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/x-swi-grammar
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
  
        test_audio = 'ground_pickup.ulaw'  
        test_grammar = "pr2000_SpeakFreelyMainMenu_DM.gram"        
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'
        test_grammar_uri = client.test_res_url + test_grammar        
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<result><interpretation grammar=.*scheduling ground pickup</input><instance><route confidence=.+>Pickup_Schedule</route><SWI_literal>scheduling ground pickup</SWI_literal>.*</instance></interpretation></result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        # test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-grammar")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test00136_Tier4GrammarFedex_default_resultFormat_default_mediaType(self):
        """
        Test Tier4 fedex grammar pr2000_SpeakFreelyMainMenu_DM.gram
        Input audio sent - ground_pickup.ulaw
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/x-swi-grammar
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = 'ground_pickup.ulaw'     
        test_grammar = "pr2000_SpeakFreelyMainMenu_DM.gram"      
        test_grammar_type = "uri_grammar"
        #test_media_type = 'srgsxml'
        test_media_type = 'xswigrammar'
        test_grammar_uri = client.test_res_url + test_grammar
        
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)        
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        time.sleep(30)
        test_result = ""
        test_expect = "<result><interpretation grammar=.*scheduling ground pickup</input><instance><route confidence=.+>Pickup_Schedule</route><SWI_literal>scheduling ground pickup</SWI_literal>.*</instance></interpretation></result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-grammar")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test00137_Tier4GrammarFedex_emma_resultFormat_default_mediaType(self):
        """
        Test Tier4 fedex grammar pr2000_SpeakFreelyMainMenu_DM.gram
        Input audio sent - ground_pickup.ulaw
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/x-swi-grammar
            c) For event SWIrslt, value of token MEDIA should be application/x-vnd.nuance.emma+xml
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'ground_pickup.ulaw'
        test_grammar = "pr2000_SpeakFreelyMainMenu_DM.gram"    
        test_grammar_type = "uri_grammar"
        test_grammar_uri = client.test_res_url + test_grammar
        test_result_format = 'emma'
        
        test_recogParams = client.recognition_parameters(resultFormat=test_result_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<emma:emma version=\"1.0\" xmlns:emma=\"http://www.w3.org/TR/2007/CR-emma-20071211\" xmlns:nuance=\"http://nr10.nuance.com/emma\"><emma:grammar id=\"grammar_1\" ref=\"" + client.test_res_url + "pr2000_SpeakFreelyMainMenu_DM.gram\"/><emma:one-of id=\"nbest\" emma:disjunction-type=\"recognition\" emma:duration=\"1954\" emma:mode=\"voice\"><emma:interpretation id=\"interp_1\" emma:confidence=.+ emma:grammar-ref=\"grammar_1\" emma:tokens=\"scheduling ground pickup\"><route conf=\"0.99\">Pickup_Schedule</route><SWI_literal>scheduling ground pickup</SWI_literal>.*</emma:emma>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-grammar")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="MEDIA", value="application/x-vnd.nuance.emma+xml")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()
            
    def test00138_Tier4GrammarFedex_InvalidMediaType(self):
        """
          Test Tier4 fedex grammar pr2000_SpeakFreelyMainMenu_DM.gram
          Input audio sent - yes.ulaw
          Expected Result: SWIrec_STATUS_NO_MATCH
        """

        client = gRPCClient()

        test_audio = 'ground_pickup.ulaw'
        test_grammar = "pr2000_SpeakFreelyMainMenu_DM.gram"       
        test_grammar_type = "uri_grammar"
        test_media_type = 'Invalid'
        test_expect4 = 'unknown enum label \"Invalid\"'
        test_grammar_uri = client.test_res_url + test_grammar
   
        try:
            test_recogParams = client.recognition_parameters()
            test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type)

        except (AssertionError, TimeoutException, Exception) as e:
            msg = "\nFound exception!\n" + str(e)
            # print(msg)
            if self.assertRecognitionResult(inputToCheck=str(e), expectResult=test_expect4):
                msg = "Test passed. Expected: \n" + msg + "\n"
                print(msg)
            else:
                self.fail(e)
                
    def test00139_Tier4GrammarFedex_noMatch(self):
        """
        Test Tier4 fedex grammar pr2000_SpeakFreelyMainMenu_DM.gram
        Input audio sent - yes.ulaw
        Expect:
        1) [Test case] NRC recognize return SWIrec_STATUS_NO_MATCH
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/x-swi-grammar
            c) For event SWIrcnd, value of Token RENR should be prun
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'
        test_grammar = "pr2000_SpeakFreelyMainMenu_DM.gram"       
        test_grammar_type = "uri_grammar"
        test_media_type = 'xswigrammar'
        test_grammar_uri = client.test_res_url + test_grammar

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_result = ""
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
        
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, result_status="NO_MATCH")
        test_record_1.set_checklist_types(["Basic", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-grammar")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RENR", value="prun")
        # test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_grammar_uri)
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test00140_UriGrammarXswiparameter_swirec_max_cpu_time_1ms(self):
        """
        Test swirec_max_cpu_time via Parameter grammar
        in parameter grammar file value of  swirec_max_cpu_time set to default as 1 ms
        Expect:
        1) [Test case] NRC recognize return SWIrec_STATUS_MAX_CPU_TIME
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/x-swi-grammar
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'
        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_max_cpu_time_1ms.grxml"
        test_media_type = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri = client.test_res_url + test_grammar  

        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "uri_grammar_yes.grxml"
        test_media_type2 = 'srgsxml'      
        test_grammar_uri2 = client.test_res_url + test_grammar2     

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)     
        test_recogRes = [test_recogRes1, test_recogRes2]     
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)
        #test_expect = "SWIrec_STATUS_MAX_CPU_TIME"
        test_expect = "CPU_TIME"       
        
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #          
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, result_status="MAX_CPU_TIME")
        test_record_1.set_checklist_types(["Grammar", "Endpointer"])
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri2)
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RENR", value="maxc")
        # test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar="+test_grammar_uri2)

        try:    
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(3)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()  
            kafka.cleanup()

    def test00141_UriGrammarXswiparameter_swirec_max_cpu_time_default(self):
        """
        Test swirec_max_cpu_time via Parameter grammar
        in parameter grammar file value of  swirec_max_cpu_time set to default as 20000 ms
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/x-swi-parameter
            c) For event SWIrcnd, value of Token RENR should be prun
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = 'yes.ulaw'      
        test_grammar_type1 = 'uri_grammar'
        test_grammar1 = "uri_grammar_yes.grxml"
        test_media_type1 = 'srgsxml'      
        test_grammar_uri1 = client.test_res_url + test_grammar1       

        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "parameter_grammar_swirec_max_cpu_time_default.grxml"
        test_media_type2 = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri2 = client.test_res_url + test_grammar2       

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1,mediaType=test_media_type1)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)       
        test_recogRes = [test_recogRes1, test_recogRes2]     
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)
        test_expect = "<result><interpretation grammar=.*{SWI_literal:yes}<\/SWI_meaning><\/instance.+\/interpretation.+\/result>"      
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri1)
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri2)
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\""+test_grammar_uri1)
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RENR", value="prun")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri1)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()      
            kafka.cleanup()

    
    def test00142_UriGrammarXswiparameter_swirec_max_cpu_time_22000ms(self):
        """
        Test swirec_max_cpu_time via Parameter grammar
        in parameter grammar file value of  swirec_max_cpu_time set to 22000 ms
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/x-swi-parameter
            c) For event SWIrcnd, value of Token RENR should be ok
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'       
        test_grammar_type1 = 'uri_grammar'
        test_grammar1 = "uri_grammar_yes.grxml"
        test_media_type1 = 'srgsxml'      
        test_grammar_uri1 = client.test_res_url + test_grammar1   

        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "parameter_grammar_swirec_max_cpu_time_22000ms.grxml"
        test_media_type2 = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri2 = client.test_res_url + test_grammar2   

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1,mediaType=test_media_type1)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)       
        test_recogRes = [test_recogRes1, test_recogRes2]       
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)
        test_expect = "<result><interpretation grammar=.*{SWI_literal:yes}<\/SWI_meaning><\/instance.+\/interpretation.+\/result>"   
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        #test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/x-swi-parameter")
        test_check1 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri1)
        test_check2 = test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri2)
        test_record_1.add_sequence_to_checklist([test_check1, test_check2])
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RENR", value="prun")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+"+test_grammar_uri1)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()  
            kafka.cleanup()      
            
    def test00143_UriGrammarXswiparameter_swirec_max_cpu_time_invalid_negative_value(self):
        """
        Test swirec_max_cpu_time via Parameter grammar
        in parameter grammar file value of  swirec_max_cpu_time set to negative integer value
        Expected Result: code:400 with Bad Request message
        """
        client = gRPCClient()
        
        test_audio = 'yes.ulaw'
        
        test_grammar_type1 = 'uri_grammar'
        test_grammar1 = "uri_grammar_yes.grxml"
        test_media_type1 = 'srgsxml'      
        test_grammar_uri1 = client.test_res_url + test_grammar1 
        
        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "parameter_grammar_swirec_max_cpu_time_Invalid.grxml"
        test_media_type2 = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri2 = client.test_res_url + test_grammar2     
             
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1,mediaType=test_media_type1)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)
        
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)

        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource"
        
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
                  
        try:
            
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)  
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()  
            time.sleep(20)
            
       
    def test00144_UriGrammarXswiparameter_swirec_max_cpu_time_invalid_value(self):
        """
        Test swirec_max_cpu_time via Parameter grammar
        in parameter grammar file value of  swirec_max_cpu_time set to invalid string
        Expected Result: code:400 with Bad Request message
        """
        client = gRPCClient()
        
        test_audio = 'yes.ulaw'
        
        test_grammar_type1 = 'uri_grammar'
        test_grammar1 = "uri_grammar_yes.grxml"
        test_media_type1 = 'srgsxml'      
        test_grammar_uri1 = client.test_res_url + test_grammar1    
        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "parameter_grammar_swirec_max_cpu_time_invalid_value.grxml"
        test_media_type2 = 'xswiparameter'      
        test_confLevel = 0
        test_grammar_uri2 = client.test_res_url + test_grammar2     

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1,mediaType=test_media_type1)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)
        
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters(confLevel=test_confLevel)

        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource"
        
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
                  
        try:
            
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)  
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)  
            

    def test00145_UriGrammarInvalidGrammarData(self):

        client = gRPCClient()
        
        test_audio = 'yes.ulaw'
        test_grammar = "uri_grammar_yes_invalid.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            time.sleep(20)


    def test00146_Https_UriGrammar_MovieScript_251(self):
        """
        Test NRC recognition URI grammar fetch via HTTPs with audio 'yes.ulaw';
        Before test harness update: this is a special case which need to have the https grammar link added/updated in testServerConfig.yaml first; Temporarily for QA test using: NRCTestResURL: 'https://10.3.104.181/SS12/'
        After test harness update:
        test_grammar_uri replace client.test_res_url with client.test_res_url_secure
        Expect:
        1) [Test case] NRC recognize return successful
        """
        client = gRPCClient()

        test_audio = 'movie.ulaw'
        test_grammar = "movies_script250.grxml"  # movies_script250.grxml
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url_secure + test_grammar

        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance>The Good, the Bad and the Ugly<SWI_meaning>The Good, the Bad and the Ugly</SWI_meaning><SWI_literal>The Good, the Bad and the Ugly</SWI_literal><SWI_grammarName>https:.+</SWI_grammarName></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()


    def test00147_Https_UriGrammarInvalidGrammarData(self):
        """
        Negative test NRC recognition invalid URI grammar fetch via HTTPs with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return unsuccessful
        """
        client = gRPCClient()
        
        test_audio = 'yes.ulaw'
        test_grammar = "uri_grammar_yes_invalid.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url_secure + test_grammar
        
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            print(msg)
            time.sleep(1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            time.sleep(20)


    def test00148_Https_UriGrammarWeight(self):
        """
        Test NRC recognition via HTTPS URI grammar with audio 'yes.ulaw' & Grammar Weight as 2
        Expect:
        1) [Test case] NRC recognize return should be successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
                a) Grammar related events all presented in the call log, including: SWIgrld;
                b) for event SWIgrld, value of Token WGHT should be matched with value of grammar weight.
        """  
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_yes.grxml"
        test_media_type = 'srgsxml'
        test_grammar_weight = 2
        test_grammar_uri = client.test_res_url_secure + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal><SWI_grammarName>https:.+uri_grammar_yes.grxml</SWI_grammarName><SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters()
        # Specifies the grammar's weight relative to other grammars active for that recognition. This value can range from 1 to 32767. Default is 1
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,mediaType=test_media_type, grammarWeight=test_grammar_weight)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="WGHT", value=test_grammar_weight)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\""+test_grammar_uri)
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()


    def test00149_Https_UriGrammarXswigrammarMediaTypefrCA(self):
        """
        Test NRC recognition via HTTPS URI grammar with audio 'oui.wav" & xswigrammar (.gram)
        Expect:
        1) [Test case] NRC recognize return should be successful
        """
        client = gRPCClient()
        
        test_audio = 'oui.wav'
        test_audio_format = 'pcm'
        test_language = 'fr-CA'
        test_media_type = 'xswigrammar'
        test_grammar = "uri_grammar_oui_fr-CA.gram"
        test_grammar_type = "uri_grammar"
        test_grammar_uri = client.test_res_url_secure + test_grammar

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>oui</SWI_literal><SWI_grammarName>https:.+uri_grammar_oui_fr-CA.gram</SWI_grammarName><SWI_meaning.+oui.+SWI_meaning></instance></interpretation></result>"
        
        try:
            
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  
           
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()


    def test00150_Https_URIGrammarEMMAResultFormat(self): 
        """
            Test NRC recognition via HTTPS URI grammar with audio 'yes.ulaw' & EMMA result format
            Expect:
            1) [Test case] NRC recognize return should be successful
        """

        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_audio_format = 'ulaw'
        test_result_format = 'emma'
        test_grammar = "uri_grammar_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'

        test_grammar_uri = client.test_res_url_secure + test_grammar
        print("Test grammar URI: " + test_grammar_uri + "\n")

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format,resultFormat=test_result_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_expect = "<emma:emma.*ref=\"https:.+uri_grammar_yes.grxml\".*{SWI_literal:yes}<\/SWI_meaning><\/emma:interpretation><\/emma:emma>"

        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()


    def test00151_Https_UriGrammarParametersShortRequestTimeout(self):
        """
            Test NRC recognition via HTTPS URI grammar with audio 'yes.ulaw' & URI Prameter requestTimeout as 2
            Expect:
            1) [Test case] NRC recognize return should give error Failed to load Recognition Resource
         """ 

        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_oui_fr - CA.grxml"
        test_media_type = 'srgsxml'
        test_requestTimeout = 2
        test_grammar_uri = client.test_res_url_secure + test_grammar

        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource "

        test_UriParams = client.recognition_UriGrammarParam(requestTimeout=test_requestTimeout)
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,mediaType=test_media_type, uriParameters=test_UriParams)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            time.sleep(20)


    def test00152_Https_UriGrammarParametersMaxAge(self):
        """
            Test NRC recognition via HTTPS URI grammar with audio 'yes.ulaw' & URI Prameter requestTimeout and max_Age = 0
            Expect:
            1) [Test case] NRC recognize return should be successful
         """ 

        client = gRPCClient()

        test_audio = 'yes.ulaw'
        test_grammar_type = "uri_grammar"
        test_grammar = "uri_grammar_yes.grxml"
        test_media_type = 'srgsxml'

        test_maxAge = 0
        test_grammar_uri = client.test_res_url_secure + test_grammar
        
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal><SWI_grammarName>https:.+uri_grammar_yes.grxml</SWI_grammarName><SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        # test_UriParams =  client.recognition_UriGrammarParam(requestTimeout=0, contentBase=test_contentBase, maxAge=0, maxStale=0)
        test_UriParams = client.recognition_UriGrammarParam(maxAge=test_maxAge)
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type, uriParameters=test_UriParams)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()


    def test00153_Https_UriGrammarXswiparameter_swirec_max_sentences_tried_Invalid_low(self):
        """
            Test NRC recognition via HTTPS URI grammar with audio '945015260.ulaw' & 2 grammars:
                - uri grammar: parameter_grammar_swirec_max_sentences_tried_Invalid_low.grxml
                - builtin grammar: digits
            Expect:
            1) [Test case] NRC recognize return should give error Failed to load Recognition Resource
        """ 
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'

        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_max_sentences_tried_Invalid_low.grxml"
        test_media_type = 'xswiparameter'      
        test_grammar_uri = client.test_res_url_secure + test_grammar     
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource at index"

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)


    def test00500_UriGrammarXswiparameterNbest_Invalid_float(self):
        """
        Negative test: Test nBest parameter with float number.
        Expect:
        1) [Test case] NRC recognize return code 400 bad request
        """
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'
        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_nBest_invalid_float.grxml"
        test_media_type = 'xswiparameter' 
        test_grammar_uri = client.test_res_url + test_grammar     
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource at index"

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]

        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)
    
    def test00501_UriGrammarXswiparameter_swirec_magic_word_conf_thresh_Invalid_float(self):
        """
        Negative test: Test threshold parameter with float number.
        Expect:
        1) [Test case] NRC recognize return code 400 bad request
        """
        client = gRPCClient()

        test_audio = '945015260.ulaw'
        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_magic_word_conf_thresh_invalid_float.grxml"
        test_media_type = 'xswiparameter'      
        test_grammar_uri = client.test_res_url + test_grammar     
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource at index"

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)
    
    def test00502_UriGrammarXswiparameter_swirec_selective_barge_in_conf_thresh_Invalid_float(self):
        """
        Negative test: Test threshold parameter with float number.
        Expect:
        1) [Test case] NRC recognize return code 400 bad request
        """
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'
        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_selective_barge_in_conf_thresh_invalid_float.grxml"
        test_media_type = 'xswiparameter'      
        test_grammar_uri = client.test_res_url + test_grammar     
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource at index"

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)

    def test00503_UriGrammarXswiparameter_swirec_max_parses_per_literal_Invalid_float(self):
        """
        Negative test: Test threshold parameter with float number.
        Expect:
        1) [Test case] NRC recognize return code 400 bad request
        """
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'
        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_max_parses_per_literal_invalid_float.grxml"
        test_media_type = 'xswiparameter'      
        test_grammar_uri = client.test_res_url + test_grammar     
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource at index"

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)

    def test00504_UriGrammarXswiparameter_swirec_max_sentences_tried_Invalid_float(self):
        """
        Negative test: Test threshold parameter with float number.
        Expect:
        1) [Test case] NRC recognize return code 400 bad request
        """
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'
        test_grammar_type1 = 'uri_grammar'
        test_grammar = "parameter_grammar_swirec_max_sentences_tried_Invalid_float.grxml"
        test_media_type = 'xswiparameter'      
        test_grammar_uri = client.test_res_url + test_grammar     
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource at index"

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes = [test_recogRes1, test_recogRes2]
        
        test_recogParams = client.recognition_swiparameters()
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)


    def test00505_BuiltinAutomaticMediaType(self):
        """
        Test NRC recognition Builtin Grammar with audio 'yes.ulaw' & Automatic MediaType
        Expect:
        1) [Test case] NRC recognize return should be successful
        """ 
        client = gRPCClient()
        test_audio = "yes.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'boolean'
        #
        test_media_type1 = None
        test_recogParams1 = client.recognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, mediaType=test_media_type1, grammarData=test_grammar_data)
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/boolean.+<instance>true<\/instance.+\/interpretation.+\/result>"
        #
        test_media_type2 = 'automatic'
        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, mediaType=test_media_type2, grammarData=test_grammar_data)
        test_recInit2 = client.recognition_init(test_recogParams2, test_recogRes2)
        test_expect2 = "<result><interpretation grammar=.+builtin:grammar\/boolean.+<instance>true<\/instance.+\/interpretation.+\/result>"

        try:

            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit2)
            time.sleep(1)

            msg = "Test result 1:\n" + test_result1 + "\n"
            msg += "Test result 2:\n" + test_result2 + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00506_BuiltinSrgsxmlMediaType(self):
        """
        Test NRC recognition Builtin Grammar with audio 'yes.ulaw' & SRGS Xml MediaType
        Expect:
        1) [Test case] NRC recognize return should be successful
        """ 

        client = gRPCClient()

        test_audio = "yes.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'boolean'
        test_media_type = 'srgsxml'
        test_recogParams = client.recognition_parameters()

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, mediaType=test_media_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/boolean.+<instance>true<\/instance.+\/interpretation.+\/result>"

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()


    def test00507_BuiltinInvalidMediaType(self):
        """
        Test NRC recognition Builtin Grammar with audio 'yes.ulaw' & Inlvalid MediaType
        Expect:
        1) [Test case] NRC recognize return should be successful
        """
        client = gRPCClient()
        test_audio = "yes.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'boolean'
        #
        test_media_type1 = 'invalid'
        test_recogParams1 = client.recognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, mediaType=test_media_type1, grammarData=test_grammar_data)
        test_recInit1 = client.recognition_init(test_recogParams1, test_recogRes1)
        test_expect1 = "<result><interpretation grammar=.+builtin:grammar\/boolean.+<instance>true<\/instance.+\/interpretation.+\/result>"
        #
        test_media_type2 = 'xxxx'
        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, mediaType=test_media_type2, grammarData=test_grammar_data)
        test_recInit2 = client.recognition_init(test_recogParams2, test_recogRes2)
        test_expect2 = "<result><interpretation grammar=.+builtin:grammar\/boolean.+<instance>true<\/instance.+\/interpretation.+\/result>"

        try:

            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit2)
            time.sleep(1)

            msg = "Test result 1:\n" + test_result1 + "\n"
            msg += "Test result 2:\n" + test_result2 + "\n"
            self.debug(msg)
            # print(msg)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()


    def test00508_UriGrammarXswiparameterMediaTypefornBest0_confLevel_high(self):
        """
        Test NRC recognition URI Grammar with audio '945015260.ulaw', XSWI parameter mediatype and high confidence level.
        Expect:
        1) [Test case] NRC recognize return should be "SWIrec_STATUS_NO_MATCH"
        """
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'
        test_grammar_type1 = 'uri_grammar'
        test_media_type = 'xswiparameter'      
        test_confLevel = 0.9
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result>.*\/result>"
        
        # Test with parameter nBest = 0.
        test_grammar0 = "parameter_grammar_nBest0.grxml"
        test_grammar_uri0 = client.test_res_url + test_grammar0
        test_recogRes01 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri0, mediaType=test_media_type)
        test_recogRes02 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes0 = [test_recogRes01, test_recogRes02]

        test_recogParams0 = client.recognition_swiparameters(confLevel=test_confLevel)
        test_recInit0 = client.recognition_init_repeated(recogParam=test_recogParams0, recogRes=test_recogRes0)

        try:
            test_result0 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit0)
            time.sleep(1)
            
            print("Test result: " + test_result0)
            self.assertRecognitionResult(inputToCheck=test_result0, expectResult=test_expect)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test00509_UriGrammarXswiparameterMediaTypefornBest3_confLevel_high(self):
        """
        Test NRC recognition URI Grammar with audio '945015260.ulaw', XSWI parameter mediatype and high confidence level.
        Expect:
        1) [Test case] NRC recognize return should be "SWIrec_STATUS_NO_MATCH"
        """
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'
        test_grammar_type1 = 'uri_grammar'
        test_media_type = 'xswiparameter'      
        test_confLevel = 0.9
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
        
        # Test with parameter nBest = 3.
        test_grammar3 = "parameter_grammar_nBest3.grxml"
        test_grammar_uri3 = client.test_res_url + test_grammar3
        test_recogRes31 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri3, mediaType=test_media_type)
        test_recogRes32 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes3 = [test_recogRes31, test_recogRes32]

        test_recogParams3 = client.recognition_swiparameters(confLevel=test_confLevel)
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams3, recogRes=test_recogRes3)

        try:
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit3)
            time.sleep(1)
  
            print("Test result 3: " + test_result3)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test00510_UriGrammarXswiparameterMediaTypefornBest5_confLevel_high(self):
        """
        Test NRC recognition URI Grammar with audio '945015260.ulaw', XSWI parameter mediatype and high confidence level.
        Expect:
        1) [Test case] NRC recognize return should be "SWIrec_STATUS_NO_MATCH"
        """
        client = gRPCClient()
        
        test_audio = '945015260.ulaw'
        test_grammar_type1 = 'uri_grammar'
        test_media_type = 'xswiparameter'      
        test_confLevel = 0.9
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"

        # Test with parameter nBest = 5.  
        test_grammar5 = "parameter_grammar_nBest5.grxml"
        test_grammar_uri5 = client.test_res_url + test_grammar5
        test_recogRes51 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri5, mediaType=test_media_type)
        test_recogRes52 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recogRes5 = [test_recogRes51, test_recogRes52]

        test_recogParams5 = client.recognition_swiparameters(confLevel=test_confLevel)
        test_recInit5 = client.recognition_init_repeated(recogParam=test_recogParams5, recogRes=test_recogRes5)

        try:
            test_result5 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit5)
            time.sleep(1)

            print("Test result 5: " + test_result5)
            self.assertRecognitionResult(inputToCheck=test_result5, expectResult=test_expect)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test089_NRIR_osr20_feature_W3CGram_Case1_Activate_Grammars_Test_Activate_Grammars(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/W3CGram/Case1_Activate_Grammars/Test_Activate_Grammars
            
            Verifies W3C compatibility.

            Expect:
            1) [Test Case]
                a) Grammar loaded NRIR_alternative-null.grxml with silence audio. Expect code 408 no-input timeout (no audio received)
        """
        client = gRPCClient()
        #
        test_audio1 = "silence.ulaw"
        test_audio_format = 'ulaw'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_alternative-null.grxml'
        test_media_type1 = 'srgsxml'
        test_expect11 = "code: 404"
        test_expect12 = 'message: \"No Speech\"'
        test_expect3 = 'details: \"No speech detected\"'
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
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test00511_NRIR_osr20_feature_W3CGram_Case1_Activate_Grammars_Test_Activate_Grammars_3_Silence(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/W3CGram/Case1_Activate_Grammars/Test_Activate_Grammars
            
            Verifies W3C compatibility. 3 grammars loaded.
            Note: Audio no input timeout parameter set to 100ms to accelerate the test.

            Expect:
                1) [Test case] 
                    a) Load 3 grammars and send silence for each recognition. Expect audio silence results.
        """
        client = gRPCClient()
        #
        test_audio = "silence.ulaw"
        test_audio_format = 'ulaw'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_expect1 = "code: 404"
        test_expect2 = 'message: \"No Speech\"'
        test_no_input_timeout = 100 # timeout for no input after 100ms 
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format, noInputTimeout=test_no_input_timeout)

        # Grammar 1 to load 
        test_grammar_data1 = 'NRIR_alternative-one-item.grxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes1)

        # Grammar 2 to load 
        test_grammar_data2 = 'NRIR_alternatives-no-weights.grxml'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes2)

        # Grammar 3 to load 
        test_grammar_data3 = 'NRIR_alternatives-one-with-weight.grxml'
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
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect2)
            #
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            #
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect2)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test00512_NRIR_osr20_feature_W3CGram_Case1_Activate_Grammars_Test_Activate_Grammars_5_Silence(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/W3CGram/Case1_Activate_Grammars/Test_Activate_Grammars
            
            Verifies W3C compatibility. 5 grammars loaded.
            Note: Audio no input timeout parameter set to 100ms to accelerate the test.

            Expect:
                1) [Test case] 
                    a) Load 5 grammars and send silence for each recognition. Expect audio silence results.
        """
        client = gRPCClient()
        #
        test_audio = "silence.ulaw"
        test_audio_format = 'ulaw'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_expect1 = "code: 404"
        test_expect2 = 'message: \"No Speech\"'
        test_no_input_timeout = 100 # timeout for no input after 100ms 
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format, noInputTimeout=test_no_input_timeout)

        # Grammar 1 to load 
        test_grammar_data1 = 'NRIR_mode-voice.grxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes1)

        # Grammar 2 to load 
        test_grammar_data2 = 'NRIR_sequence-token.grxml'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes2)

        # Grammar 3 to load 
        test_grammar_data3 = 'NRIR_repeat-0-times.grxml'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri3, mediaType=test_media_type)
        test_recogRes3 = [test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes3)

        # Grammar 4 to load 
        test_grammar_data4 = 'NRIR_repeat-n-exact.grxml'
        test_grammar_uri4 = client.test_res_url + test_grammar_data4
        test_recogRes4 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri4, mediaType=test_media_type)
        test_recogRes4 = [test_recogRes4]
        test_recInit4 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes4)

        # Grammar 5 to load 
        test_grammar_data5 = 'NRIR_rule-public.grxml'
        test_grammar_uri5 = client.test_res_url + test_grammar_data5
        test_recogRes5 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri5, mediaType=test_media_type)
        test_recogRes5 = [test_recogRes5]
        test_recInit5 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes5)
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
            test_result5 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit5)
            time.sleep(1)
            #
            msg = "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            msg += "Test recognition result 4: \n" + test_result4 + "\n"
            msg += "Test recognition result 5: \n" + test_result5 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect2)
            #
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            #
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect2)
            #
            self.assertRecognitionResult(inputToCheck=test_result4, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result4, expectResult=test_expect2)
            #
            self.assertRecognitionResult(inputToCheck=test_result5, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result5, expectResult=test_expect2)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test00513_NRIR_osr20_feature_W3CGram_Case1_Activate_Grammars_Test_Activate_Grammars_10_Silence(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/W3CGram/Case1_Activate_Grammars/Test_Activate_Grammars
            
            Verifies W3C compatibility. 10 grammars loaded.
            Note: Audio no input timeout parameter set to 100ms to accelerate the test.

            Expect:
                1) [Test case] 
                    a) Load 10 grammars and send silence for each recognition. Expect audio silence results.
        """
        client = gRPCClient()
        #
        test_audio = "silence.ulaw"
        test_audio_format = 'ulaw'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_expect1 = "code: 404"
        test_expect2 = 'message: \"No Speech\"'
        test_no_input_timeout = 100 # timeout for no input after 100ms 
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format, noInputTimeout=test_no_input_timeout)
        # test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)

        # Grammar 1 to load 
        test_grammar_data1 = 'NRIR_comment-xml.grxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes1)

        # Grammar 2 to load 
        test_grammar_data2 = 'NRIR_ruleref-local.grxml'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes2)

        # Grammar 3 to load 
        test_grammar_data3 = 'NRIR_sequence-item-whitespace.grxml'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri3, mediaType=test_media_type)
        test_recogRes3 = [test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes3)

        # Grammar 4 to load 
        test_grammar_data4 = 'NRIR_token-element.grxml'
        test_grammar_uri4 = client.test_res_url + test_grammar_data4
        test_recogRes4 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri4, mediaType=test_media_type)
        test_recogRes4 = [test_recogRes4]
        test_recInit4 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes4)

        # Grammar 5 to load 
        test_grammar_data5 = 'NRIR_doctype.grxml'
        test_grammar_uri5 = client.test_res_url + test_grammar_data5
        test_recogRes5 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri5, mediaType=test_media_type)
        test_recogRes5 = [test_recogRes5]
        test_recInit5 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes5)

        # Grammar 6 to load 
        test_grammar_data6 = 'NRIR_token-quoted.grxml'
        test_grammar_uri6 = client.test_res_url + test_grammar_data6
        test_recogRes6 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri6, mediaType=test_media_type)
        test_recogRes6 = [test_recogRes6]
        test_recInit6 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes6)

        # Grammar 7 to load 
        test_grammar_data7 = 'NRIR_tag-format-decl.grxml'
        test_grammar_uri7 = client.test_res_url + test_grammar_data7
        test_recogRes7 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri7, mediaType=test_media_type)
        test_recogRes7 = [test_recogRes7]
        test_recInit7 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes7)

        # Grammar 8 to load 
        test_grammar_data8 = 'NRIR_example-2-places.grxml'
        test_grammar_uri8 = client.test_res_url + test_grammar_data8
        test_recogRes8 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri8, mediaType=test_media_type)
        test_recogRes8 = [test_recogRes8]
        test_recInit8 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes8)

        # Grammar 9 to load 
        test_grammar_data9 = 'NRIR_language-en-us.grxml'
        test_grammar_uri9 = client.test_res_url + test_grammar_data9
        test_recogRes9 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri9, mediaType=test_media_type)
        test_recogRes9 = [test_recogRes9]
        test_recInit9 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes9)

        # Grammar 10 to load 
        test_grammar_data0 = 'NRIR_meta.grxml'
        test_grammar_uri0 = client.test_res_url + test_grammar_data0
        test_recogRes0 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri0, mediaType=test_media_type)
        test_recogRes0 = [test_recogRes0]
        test_recInit0 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes0)
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
            test_result5 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit5)
            time.sleep(1)
            test_result6 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit6)
            time.sleep(1)
            test_result7 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit7)
            time.sleep(1)
            test_result8 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit8)
            time.sleep(1)
            test_result9 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit9)
            time.sleep(1)
            test_result0 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit0)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            msg += "Test recognition result 4: \n" + test_result4 + "\n"
            msg += "Test recognition result 5: \n" + test_result5 + "\n"
            msg += "Test recognition result 6: \n" + test_result6 + "\n"
            msg += "Test recognition result 7: \n" + test_result7 + "\n"
            msg += "Test recognition result 8: \n" + test_result8 + "\n"
            msg += "Test recognition result 9: \n" + test_result9 + "\n"
            msg += "Test recognition result 10: \n" + test_result0 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect2)
            #
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            #
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect2)
            #
            self.assertRecognitionResult(inputToCheck=test_result4, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result4, expectResult=test_expect2)
            #
            self.assertRecognitionResult(inputToCheck=test_result5, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result5, expectResult=test_expect2)
            #
            self.assertRecognitionResult(inputToCheck=test_result6, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result6, expectResult=test_expect2)
            #
            self.assertRecognitionResult(inputToCheck=test_result7, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result7, expectResult=test_expect2)
            #
            self.assertRecognitionResult(inputToCheck=test_result8, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result8, expectResult=test_expect2)
            #
            self.assertRecognitionResult(inputToCheck=test_result9, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result9, expectResult=test_expect2)
            #
            self.assertRecognitionResult(inputToCheck=test_result0, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result0, expectResult=test_expect2)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test00514_NRIR_osr20_feature_W3CGram_Case1_Activate_Grammars_Test_Activate_Grammars_3(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/W3CGram/Case1_Activate_Grammars/Test_Activate_Grammars
            
            Verifies W3C compatibility. 3 grammars loaded.
            Expect:
                1) [Test case] 
                    a) Load grammar that contains "si_es-ES" and send "si" audio. Expect "si" as recognition result.
                    b) Load grammar that contains "yes_en-US" and send "yes" audio. Expect "yes" as recognition result.
                    c) Load grammar that contains "si_es-US" and send "si" audio. Expect "si" as recognition result.
        """
        client = gRPCClient()
        #
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'

        # Grammar 1 to load 
        test_audio1 = "si.ulaw.raw"
        test_audio_format1 = 'ulaw'
        test_grammar_data1 = 'uri_grammar_si_es-ES.grxml'
        test_expect1 = '<SWI_meaning>{SWI_literal:si}</SWI_meaning>'

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)

        # Grammar 2 to load 
        test_audio2 = "yes.ulaw"
        test_audio_format2 = 'ulaw'
        test_grammar_data2 = 'uri_grammar_yes.grxml'
        test_expect2 = '<SWI_meaning>{SWI_literal:yes}</SWI_meaning>'
        
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogParams2 = client.recognition_parameters(audioFormat=test_audio_format2)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams2, recogRes=test_recogRes2)
        
        # Grammar 3 to load 
        test_audio3 = "si.ulaw.raw"
        test_audio_format3 = 'ulaw'
        test_grammar_data3 = 'uri_grammar_si_es-US.grxml'
        test_expect3 = '<SWI_meaning>{SWI_literal:si}</SWI_meaning>'

        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogParams3 = client.recognition_parameters(audioFormat=test_audio_format3)
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri3)
        test_recogRes3 = [test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams3, recogRes=test_recogRes3)

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
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
            
        finally:
            client.cleanup()

    def test00515_NRIR_osr20_feature_W3CGram_Case1_Activate_Grammars_Test_Activate_Grammars_5(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/W3CGram/Case1_Activate_Grammars/Test_Activate_Grammars
            
            Verifies W3C compatibility. 5 grammars loaded.
            Expect:
                1) [Test case] 
                    a) Load digits grammar and send "01234" audio. Expect "zero one two three four" as recognition result.
                    b) Load grammar that contains "yes_en-US" and send "yes" audio. Expect "yes" as recognition result.
                    c) Load grammar that contains "si_es-US" and send "si" audio. Expect "si" as recognition result.
                    d) Load grammar about token-elemetns and send "yes" audio. Expect no match.
                    e) LOad grammar about mode-voice and send "yes" audio. Expect no match.
        """
        client = gRPCClient()
        #
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'

        # Grammar 1 to load 
        test_audio1 = "01234.ulaw"
        test_audio_format1 = 'ulaw'
        test_grammar_data1 = 'digits.grxml'
        test_expect1 = '<SWI_meaning>{SWI_literal:zero one two three four}</SWI_meaning>'

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)

        # Grammar 2 to load 
        test_audio2 = "yes.ulaw"
        test_audio_format2 = 'ulaw'
        test_grammar_data2 = 'uri_grammar_yes_robust.grxml'
        test_expect2 = '<SWI_meaning>{V:yes}</SWI_meaning>'
        
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogParams2 = client.recognition_parameters(audioFormat=test_audio_format2)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams2, recogRes=test_recogRes2)
        
        # Grammar 3 to load. 
        test_audio3 = "si.ulaw.raw"
        test_audio_format3 = 'ulaw'
        test_grammar_data3 = 'uri_grammar_si_es-US.grxml'
        test_expect3 = '<SWI_meaning>{SWI_literal:si}</SWI_meaning>'

        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogParams3 = client.recognition_parameters(audioFormat=test_audio_format3)
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri3)
        test_recogRes3 = [test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams3, recogRes=test_recogRes3)

        # Grammar 4 to load. Recognition no match
        test_audio4 = "yes.ulaw"
        test_audio_format4 = 'ulaw'
        test_grammar_data4 = 'NRIR_token-element.grxml'
        test_expect4 = 'NO_MATCH'
        #test_expect4 =  "<result>.*nomatch.*/result>"
        
        test_grammar_uri4 = client.test_res_url + test_grammar_data4
        test_recogParams4 = client.recognition_parameters(audioFormat=test_audio_format4)
        test_recogRes4 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri4)
        test_recogRes4 = [test_recogRes4]
        test_recInit4 = client.recognition_init_repeated(recogParam=test_recogParams4, recogRes=test_recogRes4)
        
        # Grammar 5 to load. Recognition no match
        test_audio5 = "yes.ulaw"
        test_audio_format5 = 'ulaw'
        test_grammar_data5 = 'NRIR_mode-voice.grxml'
        #test_expect5 = 'SWIrec_STATUS_NO_MATCH'
        test_expect5 = 'NO_MATCH'
        #test_expect5 =  "<result>.*nomatch.*/result>"

        test_grammar_uri5 = client.test_res_url + test_grammar_data5
        test_recogParams5 = client.recognition_parameters(audioFormat=test_audio_format5)
        test_recogRes5 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri5)
        test_recogRes5 = [test_recogRes5]
        test_recInit5 = client.recognition_init_repeated(recogParam=test_recogParams5, recogRes=test_recogRes5)
        #
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
            test_result5 = client.qa_nr_recognize_test_func1(audioInput=test_audio5, recInit=test_recInit5)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            msg += "Test recognition result 4: \n" + test_result4 + "\n"
            msg += "Test recognition result 5: \n" + test_result5 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)
            self.assertRecognitionResult(inputToCheck=test_result4, expectResult=test_expect4)
            self.assertRecognitionResult(inputToCheck=test_result5, expectResult=test_expect5)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
            
        finally:
            client.cleanup()

    def test00516_NRIR_osr20_feature_GrammarWeight_Grammar4(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/GrammarWeight/Grammar4
            
            This script tests an improper value for the weight parameter
            Expect:
            1) [Test case] 
                a) Load grammar with invalid weight attribute set to "abc". Expect "code 400, Bad Request, Failed to load RecognitionResource".
        """
        client = gRPCClient()

        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_audio1 = "yes.ulaw"
        test_audio_format1 = 'ulaw'
        test_grammar_data1 = 'NRIR_Grammar4.xml'

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)

        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource at index"

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            msg = "Test result:\n" + test_result1 + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            time.sleep(20)

    def test00517_NRIR_osr20_feature_GrammarWeight_Grammar_confusing_without_weight(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/GrammarWeight/Grammar_confusing_without_weight
            
            Audio utterance is close to all grammar items.
            Expect:
            1) [Test Case]
                a) The weight is now ignored. As long as there is 1 recognition result entry, the test passes.
        """
        client = gRPCClient()

        test_audio1 = "NRIR_vive.wav"
        test_audio_format1 = 'pcm'
        test_grammar_data1 = 'NRIR_Grammar_confusing_without_weight.xml'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_expect1 = "<?xml.+<result><interpretation.+confidence=.+<instance.+/instance></interpretation></result>"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            msg = "Test result:\n" + test_result1 + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00518_NRIR_osr20_feature_GrammarWeight_Grammar_not_weighted_wear(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/GrammarWeight/Grammar_not_weighted_wear

            Audio utterance is close to multiple gammar items.
            Expect:
            1) [Test Case]
                a) Ignore grammar weights. Expect all items in result. The order of the parse does not need to be in order of weight.
        """
        client = gRPCClient()

        test_audio1 = "NRIR_ware.wav"
        test_audio_format1 = 'pcm'
        test_grammar_data1 = 'NRIR_Grammar_not_weighted_wear.xml'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_expect1 = "G1_where"
        test_expect2 = "G1_wear"
        test_expect3 = "G1_ware"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            msg = "Test result:\n" + test_result1 + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00519_NRIR_osr20_feature_GrammarWeight_Grammar_weighted_wear(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/GrammarWeight/Grammar_weighted_wear
            
            Audio utterance is close to multiple gammar items.
            Expect:
            1) [Test Case]
                a) Grammar items' weights are important here. Expect all items in result. The order of the parse should be in order of weight: where -> wear -> ware
        """
        client = gRPCClient()

        test_audio1 = "NRIR_ware.wav"
        test_audio_format1 = 'pcm'
        test_grammar_data1 = 'NRIR_Grammar_weighted_wear.xml'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        # The order of instance should be precisely: where, wear, ware
        test_expect1 = ("<instance><SWI_meaning>G1_where</SWI_meaning><SWI_literal>where</SWI_literal>.+</instance>"
                    + "<instance><SWI_meaning>G1_wear</SWI_meaning><SWI_literal>wear</SWI_literal>.+</instance>"
                    + "<instance><SWI_meaning>G1_ware</SWI_meaning><SWI_literal>ware</SWI_literal>.+</instance>")

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            msg = "Test result:\n" + test_result1 + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00520_NRIR_osr20_feature_GrammarWeight_Grammar_weighted_wear_ruleref(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/GrammarWeight/Grammar_weighted_wear_ruleref

            Audio utterance is close to multiple gammar items.
            Note: This test case's grammar includes a ruleref element.
            Expect:
            1) [Test Case]
                a) Grammar items' weights are important here. Expect all items in result. The order of the parse should be in order of weight: where -> wear -> ware
        """
        client = gRPCClient()

        test_audio1 = "NRIR_ware.wav"
        test_audio_format1 = 'pcm'
        test_grammar_data1 = 'NRIR_Grammar_weighted_wear_ruleref.xml'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        # The order of instance should be precisely: where, wear, ware
        test_expect1 = ("<instance><SWI_meaning>G1_where</SWI_meaning><SWI_literal>where</SWI_literal>.+</instance>"
                    + "<instance><SWI_meaning>G1_wear</SWI_meaning><SWI_literal>wear</SWI_literal>.+</instance>"
                    + "<instance><SWI_meaning>G1_ware</SWI_meaning><SWI_literal>ware</SWI_literal>.+</instance>")

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            msg = "Test result:\n" + test_result1 + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00521_NRIR_osr20_feature_NewW3CGram_NewGrammar_mode_voice(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/NewW3CGram/NewGrammar_mode_voice
            
            In new W3C, grammar mode=speech is no longer used, but mode=voice. 
            Expect:
            1) [Test Case]
                a) Load grammar that contains banking interactions vocabulary & mode attribute set to voice. Audio says "interest". Expect successful recognition "<SWI_literal>interest</SWI_literal>"
        """
        client = gRPCClient()
    
        test_audio1 = "NRIR_interest.ulaw"
        test_audio_format1 = 'ulaw'
        test_grammar_data1 = 'NRIR_item_bank_mode.xml'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_expect1 = "<SWI_literal>interest</SWI_literal>"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            msg = "Test result:\n" + test_result1 + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00522_NRIR_proton_feature_DA_word_list_script_da_wordlist_onthefly(self):
        """
        NR IR Converted testcases:
            ./proton_feature/DA_word_list/script/da_wordlist_onthefly

            Tests grammar compilation and recognition.
            Used sgc to compile ".txt" grammar to ".gram"

            Expect:
            1) [Test Case]
                a) Load grammar containing vocab "Georgia" and audio utterance "Georgia". Expect successful recognition "<SWI_literal>Georgia</SWI_literal>"
        """
        client = gRPCClient()

        test_audio1 = "NRIR_georgia.wav"
        test_audio_format1 = 'pcm'
        test_grammar_data1 = 'NRIR_DA_word_list_simple.gram'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'xswigrammar'
        test_expect1 = "<SWI_literal>Georgia</SWI_literal>"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            msg = "Test result:\n" + test_result1 + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00523_NRIR_proton_feature_DA_word_list_script_da_wordlist_onthefly_userdict(self):
        """
        NR IR Converted testcases:
            ./proton_feature/DA_word_list/script/da_wordlist_onthefly_userdict

            Tests grammar compilation and recognition.
            Used sgc to compile ".txt" grammar to ".gram"
            Different grammars used with same audio.

            Expect:
            1) [Test Case]
                a) Audio utterance "Legrange", grammar does not contain "Legrange". Expect "<SWI_literal>ThisOneNeedsaUserDictionary</SWI_literal>" not part of the result.
                b) Audio utterance "Legrange", grammar references to another grammar that recognizes utterance as "ThisOneNeedsaUserDictionary". Expect "<SWI_literal>ThisOneNeedsaUserDictionary</SWI_literal>".
        """
        client = gRPCClient()
        test_grammar_type = 'uri_grammar'
        test_media_type = 'xswigrammar'
        # 1) a)
        test_audio1 = "NRIR_legrange.wav"
        test_audio_format1 = 'pcm'
        test_grammar_data1 = 'NRIR_DA_word_list_simple.gram'
        test_not_in_result1 = "<SWI_literal>ThisOneNeedsaUserDictionary</SWI_literal>" # Should not be recognized.
        test_expect1 = "NO_MATCH"
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        # 1) b)
        test_audio2 = "NRIR_legrange.wav"
        test_audio_format2 = 'pcm'
        test_grammar_data2 = 'NRIR_DA_word_list_userdict.gram'
        test_expect2 = "<SWI_literal>ThisOneNeedsaUserDictionary</SWI_literal>"
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogParams2 = client.recognition_parameters(audioFormat=test_audio_format2)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams2, recogRes=test_recogRes2)

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)

            msg = "Test result:\n" + test_result1 + "\n"
            msg += "Test result:\n" + test_result2 + "\n"
            print(msg)
            
            self.assertNotRecognitionResult(inputToCheck=test_result1, undesiredResult=test_not_in_result1)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00524_NRIR_osr20_feature_DigitConstraints_DigitConstraints2(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/DigitConstraints/DigitConstraints2

        This test excercises changes in the digits built-in grammar, particularly the usage of constraints.
        Expect:
            1) [Test Case]
                a) Activate digits builtin grammar with constraints, send audio "2", expect successful recognition.
                b) Activate digits builtin grammar with constraints, send audio "8", expect successful recognition.
                c) Activate digits builtin grammar with constraints, send audio "1" not part of constraints list, expect no match.
                d) Activate digits builtin grammar with constraints, send audio "5" not part of constraints list, expect no match.
        """
        client = gRPCClient()
        #
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits?entries=' + client.test_res_url + 'NRIR_simple_constraints.txt'
        
        # Valid recognition.
        test_audio1 = "NRIR_2.wav"
        test_expect1 = "<instance>2</instance>"
        test_audio_format1 = 'pcm'
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        
        # Valid Recognition.
        test_audio2 = "NRIR_8.wav"
        test_expect2 = "<instance>8</instance>"
        test_audio_format2 = 'pcm'
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recogParams2 = client.recognition_parameters(audioFormat=test_audio_format2)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams2, recogRes=test_recogRes2)
        
        # Invalid Recognition.
        test_audio3 = "NRIR_1.wav"
        test_audio_format3 = 'pcm'
        #test_expect3 = "SWIrec_STATUS_NO_MATCH"
        test_expect3 = "NO_MATCH"
        #test_expect3 =  "<result>.*nomatch.*/result>"
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recogParams3 = client.recognition_parameters(audioFormat=test_audio_format3)
        test_recogRes3 = [test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams3, recogRes=test_recogRes3)

        # Invalid Recognition.
        test_audio4 = "NRIR_5.wav"
        #test_expect4 = "SWIrec_STATUS_NO_MATCH"
        test_expect4 = "NO_MATCH"
        #test_expect4 =  "<result>.*nomatch.*/result>"
        test_audio_format4 = 'pcm'
        test_recogRes4 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recogParams4 = client.recognition_parameters(audioFormat=test_audio_format4)
        test_recogRes4 = [test_recogRes4]
        test_recInit4 = client.recognition_init_repeated(recogParam=test_recogParams4, recogRes=test_recogRes4)
        #
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

    def test00525_NRIR_osr20_feature_NewW3CGram_NewGrammar_pizza(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/NewW3CGram/NewGrammar_pizza
            
        The grammar loaded here, pizza.xml cantains repeat and repeat-prob which are new W3C syntax.
        Each recognition request appends a new item to the utterance.
        Expect:
            1) [Test Case]
                a) Load grammar pizza. Audio utterance "very big pizza". Expect successful recognition.
                b) Load grammar pizza. Audio utterance "very big pizza with olives". Expect successful recognition.
                c) Load grammar pizza. Audio utterance "very big pizza with olives and extra cheese". Expect successful recognition.
                d) Load grammar pizza. Audio utterance "very big pizza with olives and extra cheese and ham". Expect successful recognition.
        """
        client = gRPCClient()
        
        test_grammar_data = 'NRIR_pizza.xml'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar_data
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recogRes = [test_recogRes]
        #
        test_audio1 = "NRIR_very_big_pizza.wav"
        test_audio_format1 = "pcm"
        test_expect1 = "<SWI_literal>very big pizza</SWI_literal>"
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes)
        #
        test_audio2 = "NRIR_very_big_pizza_with_olives.wav"
        test_audio_format2 = "pcm"
        test_expect2 = "<SWI_literal>very big pizza with olives</SWI_literal>"
        test_recogParams2 = client.recognition_parameters(audioFormat=test_audio_format2)
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams2, recogRes=test_recogRes)
        #
        test_audio3 = "NRIR_very_big_pizza_with_olives_and_extra_cheese.wav"
        test_audio_format3 = "pcm"
        test_expect3 = "<SWI_literal>very big pizza with olives and extra cheese</SWI_literal>"
        test_recogParams3 = client.recognition_parameters(audioFormat=test_audio_format3)
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams3, recogRes=test_recogRes)
        #
        test_audio4 = "NRIR_very_big_pizza_with_olives_and_extra_cheese_and_ham.wav"
        test_audio_format4 = "pcm"
        test_expect4 = "<SWI_literal>very big pizza with olives and extra cheese and ham</SWI_literal>"
        test_recogParams4 = client.recognition_parameters(audioFormat=test_audio_format4)
        test_recInit4 = client.recognition_init_repeated(recogParam=test_recogParams4, recogRes=test_recogRes)
        #
        test_audio5 = "NRIR_very_very_big_pizza.wav"
        test_audio_format5 = "pcm"
        #test_expect5 = "SWIrec_STATUS_NO_MATCH"
        test_expect5 = "NO_MATCH"
        #test_expect5 =  "<result>.*nomatch.*/result>"
        test_recogParams5 = client.recognition_parameters(audioFormat=test_audio_format5)
        test_recInit5 = client.recognition_init_repeated(recogParam=test_recogParams5, recogRes=test_recogRes)
        #
        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio3, recInit=test_recInit3)
            test_result4 = client.qa_nr_recognize_test_func1(audioInput=test_audio4, recInit=test_recInit4)
            test_result5 = client.qa_nr_recognize_test_func1(audioInput=test_audio5, recInit=test_recInit5)
            #
            msg = ""
            msg += "Test result 1:\n" + test_result1 + "\n"
            msg += "Test result 2:\n" + test_result2 + "\n"
            msg += "Test result 3:\n" + test_result3 + "\n"
            msg += "Test result 4:\n" + test_result4 + "\n"
            msg += "Test result 5:\n" + test_result5 + "\n"
            print(msg)
            #
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)
            self.assertRecognitionResult(inputToCheck=test_result4, expectResult=test_expect4)
            self.assertRecognitionResult(inputToCheck=test_result5, expectResult=test_expect5)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00526_NRIR_proton_feature_DA_word_list_script_da_wordlist_weighted(self):
        """
        NR IR Converted testcases:
            ./proton_feature/DA_word_list/script/da_wordlist_weighted

        Test grammar when different weights but same audio 'NRIR_georgia.wav'
        Expect:
        1) [Test case] 
            a) NRC recognizes Georgia with unweighted (simple) grammar.
            b) NRC does NOT recognize Georgia with weighted grammar: Georgia set to -1000.
        
        parameters ignored:
        - swirec_load_adjusted_speedvsaccuracy because set to "idle", DEFAULT VALUE
        """
        client = gRPCClient()
        test_grammar_type = 'uri_grammar'
        test_media_type = 'xswigrammar'
        # 1) a)
        test_audio1 = "NRIR_georgia.wav"
        test_audio_format1 = 'pcm'
        test_grammar_data1 = 'NRIR_DA_word_list_simple.gram'
        test_expect1 = "<SWI_meaning>Georgia</SWI_meaning>"
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        # 1) b)
        test_audio2 = "NRIR_georgia.wav"
        test_audio_format2 = 'pcm'
        test_grammar_data2 = 'NRIR_DA_word_list_weighted_1.gram'
        test_not_in_result2 = "<SWI_meaning>Georgia</SWI_meaning>" # Should not be recognized.
        test_expect2 = "NO_MATCH"

        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogParams2 = client.recognition_parameters(audioFormat=test_audio_format2)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams2, recogRes=test_recogRes2)

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            #
            msg = "Test result 1:\n" + test_result1 + "\n"
            msg += "Test result 2:\n" + test_result2 + "\n"
            print(msg)
            #
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertNotRecognitionResult(inputToCheck=test_result2, undesiredResult=test_not_in_result2)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00527_NRIR_osr20_feature_GrammarWeight_Grammar_confusing_with_weight(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/GrammarWeight/Grammar_confusing_with_weight
            
        parameters ignored:
        - swirec_load_adjusted_speedvsaccuracy because set to "idle", DEFAULT VALUE
        - swi_lmweight because set to 1.0, DEFAULT VALUE

        Audio input "five" can be heard as five or hive or vive.
        Expect:
        1) [Test Case]
            a) Only return top 1 best recognition expect the vocabulary item with the higher weight: G1_vive.
        """
        client = gRPCClient()

        test_audio1 = "NRIR_vive.wav"
        test_audio_format1 = 'pcm'
        test_grammar_data1 = 'NRIR_Grammar_confusing_with_weight.xml'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_nBest1 = 1
        test_expect1 = "<SWI_meaning>G1_vive</SWI_meaning>"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1, nBest=test_nBest1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            msg = "Test result:\n" + test_result1 + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00528_NRIR_osr_quantum_feature_Multiword_Pronunciation_MultiWord_Pronun_1_en_us_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/Multiword_Pronunciation/MultiWord_Pronun_1_en_us_PERL
        
        Expect:
        1) [Test Case]
            a) Mulitiword replace. In the root grammar, swirec_multiword_replace has been set to 1. Expect recognition returned for blue_elephant_flies.wav should not be "blue elephant flies"
            
        parameters ignored:
        - swirec_load_adjusted_speedvsaccuracy because set to "idle", DEFAULT VALUE
        - SWIrecAcousticStateReset REC
        """
        client = gRPCClient()

        test_audio1 = "NRIR_blue_elephant_flies.wav"
        test_audio_format1 = 'pcm'
        test_grammar_data1 = 'NRIR_MultiWord_Pronun_1-en-us_.grxml'
        test_grammar_type = 'uri_grammar'
        test_not_in_result1 = "{SWI_literal:blue elephant flies}"
        test_expect1 = "NO_MATCH"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            msg = "Test result:\n" + test_result1 + "\n"
            print(msg)
            self.assertNotRecognitionResult(inputToCheck=test_result1, undesiredResult=test_not_in_result1)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00529_NRIR_osr_quantum_feature_Multiword_Pronunciation_MultiWord_Pronun_2_en_us_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/Multiword_Pronunciation/MultiWord_Pronun_2_en_us_PERL
        
        Expect:
        1) [Test Case]
            a) Mulitiword add. In the root grammar, swirec_multiword_replace has been set to 0. Expect recognition returned for brain_busters_bonus.wav should be "brain busters bonus"
        """
        client = gRPCClient()

        test_audio1 = "NRIR_brain_busters_bonus.wav"
        test_audio_format1 = 'pcm'
        test_grammar_data1 = 'NRIR_MultiWord_Pronun_2-en-us.grxml'
        test_grammar_type = 'uri_grammar'
        test_expect1 = "{SWI_literal:brain busters bonus}"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            msg = "Test result:\n" + test_result1 + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00530_NRIR_osr_quantum_feature_Multiword_Pronunciation_MultiWord_Pronun_3_en_us_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/Multiword_Pronunciation/MultiWord_Pronun_3_en_us_PERL
        
            Expect:
            1) [Test Case]
                a) Replace imports replace. The root grammar imports another grammar file and both have swirec_multiword_replace set to 1. Expect recognition returned should not be "he would like information about uh lost baggage"
        """
        client = gRPCClient()

        test_audio1 = "NRIR_he_would_like_information_about_uh_lost_baggage.wav"
        test_audio_format1 = 'pcm'
        test_grammar_data1 = 'NRIR_MultiWord_Pronun_3-en-us.grxml?SWI_import.IMPORTME=' + client.test_res_url + 'NRIR_MultiWord_Pronun_3_1-en-us.grxml'
        test_grammar_type = 'uri_grammar'
        test_not_in_result1 = "{SWI_literal:he would like information about uh lost baggage}"
        test_expect1 = "NO_MATCH"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            msg = "Test result:\n" + test_result1 + "\n"
            print(msg)
            self.assertNotRecognitionResult(inputToCheck=test_result1, undesiredResult=test_not_in_result1)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00531_NRIR_osr_quantum_feature_Multiword_Pronunciation_MultiWord_Pronun_4_en_us_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/Multiword_Pronunciation/MultiWord_Pronun_4_en_us_PERL
        
            Expect:
            1) [Test Case]
                a) The root grammar imports another grammar file and both have swirec_multiword_replace set to 0. Expect recognition returned should be "he would like information about uh lost baggage"
        """
        client = gRPCClient()

        test_audio1 = "NRIR_he_would_like_information_about_uh_lost_baggage.wav"
        test_audio_format1 = 'pcm'
        test_grammar_data1 = 'NRIR_MultiWord_Pronun_4-en-us.grxml?SWI_import.IMPORTME=' + client.test_res_url + 'NRIR_MultiWord_Pronun_4_1-en-us.grxml'
        test_grammar_type = 'uri_grammar'
        test_expect1 = "{SWI_literal:he would like information about uh lost baggage}"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            msg = "Test result:\n" + test_result1 + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00532_NRIR_osr_quantum_feature_Multiword_Pronunciation_MultiWord_Pronun_5_en_us_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/Multiword_Pronunciation/MultiWord_Pronun_5_en_us_PERL
        
            Expect:
            1) [Test Case] 
                a) The root grammar imports another grammar file and both have swirec_multiword_replace set to 0. Expect recognition returned should be "he would like information about uh lost baggage"
        """
        client = gRPCClient()

        test_audio1 = "NRIR_he_would_like_information_about_uh_lost_baggage.wav"
        test_audio_format1 = 'pcm'
        test_grammar_data1 = 'NRIR_MultiWord_Pronun_5-en-us.grxml?SWI_import.IMPORTME=' + client.test_res_url + 'NRIR_MultiWord_Pronun_5_1-en-us.grxml'
        test_grammar_type = 'uri_grammar'
        test_expect1 = "{SWI_literal:he would like information about uh lost baggage}"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            msg = "Test result:\n" + test_result1 + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00533_NRIR_osr_quantum_feature_Multiword_Pronunciation_MultiWord_Pronun_6_en_us_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/Multiword_Pronunciation/MultiWord_Pronun_6_en_us_PERL
        
            Expect:
            1) [Test Case]
                a) Replace imports replace. The root grammar imports another grammar file and both have swirec_multiword_replace set to 1. Expect recognition returned should not be "he would like information about uh lost baggage"

        parameters ignored:
        - swirec_load_adjusted_speedvsaccuracy because set to "idle", DEFAULT VALUE
        - SWIrecAcousticStateReset REC
        """
        client = gRPCClient()

        test_audio1 = "NRIR_he_would_like_information_about_uh_lost_baggage.wav"
        test_audio_format1 = 'pcm'
        test_grammar_data1 = 'NRIR_MultiWord_Pronun_6-en-us.grxml?SWI_import.IMPORTME=' + client.test_res_url + 'NRIR_MultiWord_Pronun_6_1-en-us.grxml'
        test_nBest1 = 1
        test_grammar_type = 'uri_grammar'
        test_not_in_result1 = "{SWI_literal:he would like information about uh lost baggage}"
        test_expect1 = "NO_MATCH"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1, nBest=test_nBest1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            msg = "Test result:\n" + test_result1 + "\n"
            print(msg)
            self.assertNotRecognitionResult(inputToCheck=test_result1, undesiredResult=test_not_in_result1)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00534_NRIR_osr_quantum_feature_Multiword_Pronunciation_MultiWord_Pronun_7_en_us_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/Multiword_Pronunciation/MultiWord_Pronun_7_en_us_PERL
        
            Expect:
            1) [Test Case]
                a) The root grammar imports another grammar file. The imported grammar has swirec_multiword_replace set to 0 and the root grammar has swirec_multiword_replace set to 1. 
                   The multiword is present in the imported grammar. Expect recognition returned should be "he would like information about uh lost baggage"
        """
        client = gRPCClient()

        test_audio1 = "NRIR_he_would_like_information_about_uh_lost_baggage.wav"
        test_audio_format1 = 'pcm'
        test_grammar_data1 = 'NRIR_MultiWord_Pronun_7-en-us.grxml?SWI_import.IMPORTME=' + client.test_res_url + 'NRIR_MultiWord_Pronun_7_1-en-us.grxml'
        test_grammar_type = 'uri_grammar'
        test_expect1 = "{SWI_literal:he would like information about uh lost baggage}"

        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)

        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            msg = "Test result:\n" + test_result1 + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00535_NRIR_osr20_feature_parameter_User_Defined_Baseline_Test_User_Defined_Baseline_PERL(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/parameter/User_Defined_Baseline/Test_User_Defined_Baseline_PERL

        parameters ignored:
        - Unable to sets ENVIRONMENT variable SWIUSERCFG mentioned in test case comment
        
        Expect:
        1) [Test Case]
            a) Audio has invalid frequency. Expect "code 408: No-Input timeout"
        """
        client = gRPCClient()
        #
        test_audio1 = "NRIR_apple.wav"
        test_audio_format1 = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_apple_orange.grxml'
        test_media_type1 = 'srgsxml'
        test_not_in_result1 = "{officeitem:apple}"
        test_expect1 = "code: 404"
        test_expect2 = 'message: \"No Speech\"'

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
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            #
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect2)
            self.assertNotRecognitionResult(inputToCheck=test_result1, undesiredResult=test_not_in_result1)
    
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test00536_NRIR_osr20_feature_GrammarWeight_Grammar1(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/GrammarWeight/Grammar1

        Test case verifies recognition results are complete regardless of the grammar loading/activation order.
        Expect:
        1) [Test Case]
            a) pass grammars in specific order. Expect items from both grammars in result.
            b) pass grammars in opposite order. Expect items from both grammars in result.
        """
        client = gRPCClient()
        
        test_audio = 'NRIR_vive.wav'
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar1 = "NRIR_Grammar1.xml"
        test_media_type1 = 'srgsxml'      
        test_grammar_uri1 = client.test_res_url + test_grammar1 

        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "NRIR_Grammar2.xml"
        test_media_type2 = 'srgsxml'
        test_grammar_uri2 = client.test_res_url + test_grammar2 
        test_expect1 = "G1_five"
        test_expect2 = "G2_five"

        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1,mediaType=test_media_type1)
        #
        test_recogRes_1 = [test_recogRes1, test_recogRes2]
        test_recogRes_2 = [test_recogRes2, test_recogRes1]
        #
        test_recogParams = client.recognition_swiparameters(audioFormat=test_audio_format)
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_1)
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_2)
                  
        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit2)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            print(msg)
            #
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test00537_NRIR_osr20_feature_GrammarWeight_Grammar2(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/GrammarWeight/Grammar2

        Test case verifies recognition results respect weights order regardless of the grammar loading/activation order.
        Expect:
        1) [Test Case]
            a) pass grammars in specific order. Expect order of result entries: G2_five, then G5_five.
            b) pass grammars in opposite order. Expect order of result entries: G2_five, then G5_five.
        """
        client = gRPCClient()
        
        test_audio = 'NRIR_vive.wav'
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar1 = "NRIR_Grammar5.xml"
        test_media_type1 = 'srgsxml'      
        test_grammar_uri1 = client.test_res_url + test_grammar1 

        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "NRIR_Grammar2.xml"
        test_media_type2 = 'srgsxml'
        test_grammar_uri2 = client.test_res_url + test_grammar2 
        test_expect1 = ("<instance><SWI_meaning>G2_five</SWI_meaning>.+</instance>.+"
                    + "<instance><SWI_meaning>G5_five</SWI_meaning>.+</instance>")

        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1,mediaType=test_media_type1)
        #
        test_recogRes_1 = [test_recogRes1, test_recogRes2]
        test_recogRes_2 = [test_recogRes2, test_recogRes1]
        #
        test_recogParams = client.recognition_swiparameters(audioFormat=test_audio_format)
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_1)
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_2)
                  
        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit2)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            print(msg)
            #
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test00538_NRIR_osr20_feature_GrammarWeight_Grammar3(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/GrammarWeight/Grammar2

        Grammar1.xml has weights at default (1.0).
        Grammar3.xml has weight of "five" at 1.0 and a decoy @ 1.5.  Becaue of normalizations, the decoy @ 1.5 will make the weight of "five" < 1.0.  This should cause G3_five to be second.

        Test case verifies recognition results respect weights order regardless of the grammar loading/activation order.
        Expect:
        1) [Test Case]
            a) pass grammars in specific order. Expect order of result entries: G1_five, then G3_five.
            b) pass grammars in opposite order. Expect order of result entries: G1_five, then G3_five.

        parameters ignored:
            - swirec_load_adjusted_speedvsaccuracy idle
        """
        client = gRPCClient()
        
        test_audio = 'NRIR_vive.wav'
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar1 = "NRIR_Grammar1.xml"
        test_media_type1 = 'srgsxml'      
        test_grammar_uri1 = client.test_res_url + test_grammar1 

        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "NRIR_Grammar3.xml"
        test_media_type2 = 'srgsxml'
        test_grammar_uri2 = client.test_res_url + test_grammar2 
        test_expect1 = ("<instance><SWI_meaning>G1_five</SWI_meaning>.+</instance>.+"
                    + "<instance><SWI_meaning>G3_five</SWI_meaning>.+</instance>")

        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2,mediaType=test_media_type2)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1,mediaType=test_media_type1)
        #
        test_recogRes_1 = [test_recogRes1, test_recogRes2]
        test_recogRes_2 = [test_recogRes2, test_recogRes1]
        #
        test_recogParams = client.recognition_swiparameters(audioFormat=test_audio_format)
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_1)
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_2)
                  
        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit2)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            print(msg)
            #
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test00539_NRIR_osr20_feature_GrammarWeight_GrammarActivate_w_weight_wear(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/GrammarWeight/Grammar2

        Set recognition parameter grammar_weight override the grammar internal weights.
        Expect:
        1) [Test Case]
            a) grammars are activated with 3 different weights, the ambiguous result should be in order of the amount of weight: where, then wear, then ware 
        """
        client = gRPCClient()
        
        test_audio = 'NRIR_ware.wav'
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar1 = "NRIR_Grammar_where.xml"
        test_media_type1 = 'srgsxml'
        test_grammar_weight1 = 30
        test_grammar_uri1 = client.test_res_url + test_grammar1 

        test_grammar_type2 = 'uri_grammar'
        test_grammar2 = "NRIR_Grammar_wear.xml"
        test_media_type2 = 'srgsxml'
        test_grammar_weight2 = 20
        test_grammar_uri2 = client.test_res_url + test_grammar2 
        
        test_grammar_type3 = 'uri_grammar'
        test_grammar3 = "NRIR_Grammar_ware.xml"
        test_media_type3 = 'srgsxml'
        test_grammar_weight3 = 10
        test_grammar_uri3 = client.test_res_url + test_grammar3 
        
        test_expect1 = ("<instance><SWI_meaning>{SWI_literal:where}</SWI_meaning>.+</instance>.+"
                    + "<instance><SWI_meaning>{SWI_literal:wear}</SWI_meaning>.+</instance>.+"
                    + "<instance><SWI_meaning>{SWI_literal:ware}</SWI_meaning>.+</instance>")

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1, grammarWeight=test_grammar_weight1)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2, mediaType=test_media_type2, grammarWeight=test_grammar_weight2)
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_uri3, mediaType=test_media_type3, grammarWeight=test_grammar_weight3)
        
        test_recogRes_1 = [test_recogRes1, test_recogRes2, test_recogRes3]
        test_recogParams = client.recognition_swiparameters(audioFormat=test_audio_format)
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_1)
                  
        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            print(msg)
            #
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test00540_NRIR_osr20_feature_LateBinding_Case1_Import_2nonterminal(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/LateBinding/Case1/Import_2nonterminal

            This test demonstrates the (dynamic) late binding of grammars as well as 
            capability to pass key/values pairs into the grammars from the query string.

            Load a grammar that references two non-terminals from two other grammars. This
            is accomplished by specifying the non-terminals (and their defining grammars)
            in the URL query string   The vocabulary items from the importing grammar, as 
            well as the imported grammars should be recognized. Then, the importing grammar
            is deactivated and reactivated using different values for variables passed in
            the query string. The grammars are written with conditional logic such that new
            values should effectively disallow certain vocabulary items intended for suppression.

            Expect:
            1) [Test Case]
                a) key1 = 1 which is !> 1 and key2 = 2 which is !> 2. Expect file, computer, monitor recognized.
                b) key1 = 2 which is > 1 and key2 = 3 which is > 2. Expect file recognized. Expect computer & monitor disallowed.

            parameter ignored:
            - swirec_load_adjusted_speedvsaccuracy idle
        """
        client = gRPCClient()
        test_audio_format = 'pcm'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)

        # Since key1 = 1 which is !> 1 and key2 = 2 which is !> 2, all the three ITEM are allowed
        test_grammar_data1 = 'NRIR_gram0.xml?SWI_import.term1=' + client.test_res_url + 'NRIR_gram1_key1.xml%3FSWI_vars.key1%3D1;SWI_import.term2=' + client.test_res_url + 'NRIR_gram2_key2.xml%3FSWI_vars.key2%3D2'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams, recogRes=test_recogRes1)
        # ITEM in gram0 - should be recognized
        test_audio11 = "NRIR_file.wav"
        test_expect11 = "<SWI_meaning>{officeitem:file}</SWI_meaning>"
        # ITEM in gram1 - should be recognized
        test_audio12 = "NRIR_computer.wav"
        test_expect12 = "<SWI_meaning>{officeitem:computer}</SWI_meaning>"
        # ITEM in gram2 - should be recognized
        test_audio13 = "NRIR_monitor.wav"
        test_expect13 = "<SWI_meaning>{officeitem:monitor}</SWI_meaning>"
        
        # Since key1 = 2 which is > 1 and key2 = 3 which is > 2
        test_grammar_data2 = 'NRIR_gram0.xml?SWI_import.term1=' + client.test_res_url + 'NRIR_gram1_key1.xml%3FSWI_vars.key1%3D2;SWI_import.term2=' + client.test_res_url + 'NRIR_gram2_key2.xml%3FSWI_vars.key2%3D3'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams, recogRes=test_recogRes2)
        # ITEM in gram0 - should be recognized
        test_audio21 = "NRIR_file.wav"
        test_expect21 = "<SWI_meaning>{officeitem:file}</SWI_meaning>"
        # ITEM in gram1 - should be disallowed
        test_audio22 = "NRIR_computer.wav"
        test_not_in_result22 = "<SWI_meaning>{officeitem:computer}</SWI_meaning>"
        # ITEM in gram2 - should be disallowed
        test_audio23 = "NRIR_monitor.wav"
        test_not_in_result23 = "<SWI_meaning>{officeitem:monitor}</SWI_meaning>"
        #
        try:
            #
            test_result11 = client.qa_nr_recognize_test_func1(audioInput=test_audio11, recInit=test_recInit1)
            time.sleep(1)
            test_result12 = client.qa_nr_recognize_test_func1(audioInput=test_audio12, recInit=test_recInit1)
            time.sleep(1)
            test_result13 = client.qa_nr_recognize_test_func1(audioInput=test_audio13, recInit=test_recInit1)
            time.sleep(1)
            #
            test_result21 = client.qa_nr_recognize_test_func1(audioInput=test_audio21, recInit=test_recInit2)
            time.sleep(1)
            test_result22 = client.qa_nr_recognize_test_func1(audioInput=test_audio22, recInit=test_recInit2)
            time.sleep(1)
            test_result23 = client.qa_nr_recognize_test_func1(audioInput=test_audio23, recInit=test_recInit2)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result11 + "\n"
            msg += "Test recognition result 2: \n" + test_result12 + "\n"
            msg += "Test recognition result 3: \n" + test_result13 + "\n"
            msg += "Test recognition result 4: \n" + test_result21 + "\n"
            msg += "Test recognition result 5: \n" + test_result22 + "\n"
            msg += "Test recognition result 6: \n" + test_result23 + "\n"
            # self.debug(msg)
            # print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result11, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result12, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result13, expectResult=test_expect13)
            #
            self.assertRecognitionResult(inputToCheck=test_result21, expectResult=test_expect21)
            self.assertNotRecognitionResult(inputToCheck=test_result22, undesiredResult=test_not_in_result22)
            self.assertNotRecognitionResult(inputToCheck=test_result23, undesiredResult=test_not_in_result23)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00541_NRIR_osr20_feature_LateBinding_Case1_Import_2nonterminal_change01(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/LateBinding/Case1/Import_2nonterminal_change01

            Load a grammar that references two non-terminals from two other grammars (using
            late-binding) and recognize against it.  Now change the importing grammar and 
            one of the imported grammars at the same time. Reactivate and recognize against
            the grammar. The changed grammars should be reloaded, but the one unchanged 
            imported grammar should not be reloaded.

            Expect:
            1) [Test Case]
                a) key1 = 1 which is !> 1 and key2 = 2 which is !> 2. Expect file, computer, monitor recognized.
                b) key1 = 2 which is > 1 and key2 = 3 which is > 2. Expect file, apple, monitor, orange recognized. Expect computer not recognized.

            parameter ignored:
            - swirec_load_adjusted_speedvsaccuracy idle
        """
        client = gRPCClient()
        test_audio_format = 'pcm'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)

        # Since key1 = 1 which is !> 1 and key2 = 2 which is !> 2, all the three ITEM are allowed
        test_grammar_data1 = 'NRIR_gramA_1.xml?SWI_import.term1=' + client.test_res_url + 'NRIR_gramB_1.xml%3FSWI_vars.key1%3D1;SWI_import.term2=' + client.test_res_url + 'NRIR_gram2_key2.xml%3FSWI_vars.key2%3D2'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams, recogRes=test_recogRes1)
        # ITEM in gram0 - should be recognized
        test_audio11 = "NRIR_file.wav"
        test_expect11 = "<SWI_meaning>{officeitem:file}</SWI_meaning>"
        # ITEM in gram1 - should be recognized
        test_audio12 = "NRIR_computer.wav"
        test_expect12 = "<SWI_meaning>{officeitem:computer}</SWI_meaning>"
        # ITEM in gram2 - should be recognized
        test_audio13 = "NRIR_monitor.wav"
        test_expect13 = "<SWI_meaning>{officeitem:monitor}</SWI_meaning>"
        
        # Since key1 = 2 which is > 1 and key2 = 3 which is > 2
        test_grammar_data2 = 'NRIR_gramA_2.xml?SWI_import.term1=' + client.test_res_url + 'NRIR_gramB_2.xml%3FSWI_vars.key1%3D1;SWI_import.term2=' + client.test_res_url + 'NRIR_gram2_key2.xml%3FSWI_vars.key2%3D2'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams, recogRes=test_recogRes2)
        # File should NOT be recognized
        test_audio21 = "NRIR_file.wav"
        test_not_in_result21 = "<SWI_meaning>{officeitem:file}</SWI_meaning>"
        # Apple should be recognized
        test_audio22 = "NRIR_apple_8kHz.wav"
        test_expect22 = "<SWI_meaning>{officeitem:apple}</SWI_meaning>"
        # Computer should NOT be recognized
        test_audio23 = "NRIR_computer.wav"
        test_not_in_result23 = "<SWI_meaning>{officeitem:computer}</SWI_meaning>"
        # Monitor should be recognized
        test_audio24 = "NRIR_monitor.wav"
        test_expect24 = "<SWI_meaning>{officeitem:monitor}</SWI_meaning>"
        # Orange should be recognized
        test_audio25 = "NRIR_orange.wav"
        test_expect25 = "<SWI_meaning>{officeitem:orange}</SWI_meaning>"
        # Monitor should be recognized
        test_audio26 = "NRIR_monitor.wav"
        test_expect26 = "<SWI_meaning>{officeitem:monitor}</SWI_meaning>"
        #
        try:
            #
            test_result11 = client.qa_nr_recognize_test_func1(audioInput=test_audio11, recInit=test_recInit1)
            time.sleep(1)
            test_result12 = client.qa_nr_recognize_test_func1(audioInput=test_audio12, recInit=test_recInit1)
            time.sleep(1)
            test_result13 = client.qa_nr_recognize_test_func1(audioInput=test_audio13, recInit=test_recInit1)
            time.sleep(1)
            test_result21 = client.qa_nr_recognize_test_func1(audioInput=test_audio21, recInit=test_recInit2)
            time.sleep(1)
            test_result22 = client.qa_nr_recognize_test_func1(audioInput=test_audio22, recInit=test_recInit2)
            time.sleep(1)
            test_result23 = client.qa_nr_recognize_test_func1(audioInput=test_audio23, recInit=test_recInit2)
            time.sleep(1)
            test_result24 = client.qa_nr_recognize_test_func1(audioInput=test_audio24, recInit=test_recInit2)
            time.sleep(1)
            test_result25 = client.qa_nr_recognize_test_func1(audioInput=test_audio25, recInit=test_recInit2)
            time.sleep(1)
            test_result26 = client.qa_nr_recognize_test_func1(audioInput=test_audio26, recInit=test_recInit2)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result11 + "\n"
            msg += "Test recognition result 2: \n" + test_result12 + "\n"
            msg += "Test recognition result 3: \n" + test_result13 + "\n"
            msg += "Test recognition result 4: \n" + test_result21 + "\n"
            msg += "Test recognition result 5: \n" + test_result22 + "\n"
            msg += "Test recognition result 6: \n" + test_result23 + "\n"
            msg += "Test recognition result 7: \n" + test_result24 + "\n"
            msg += "Test recognition result 8: \n" + test_result25 + "\n"
            msg += "Test recognition result 9: \n" + test_result26 + "\n"
            # self.debug(msg)
            # print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result11, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result12, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result13, expectResult=test_expect13)
            #
            self.assertNotRecognitionResult(inputToCheck=test_result21, undesiredResult=test_not_in_result21)
            self.assertRecognitionResult(inputToCheck=test_result22, expectResult=test_expect22)
            self.assertNotRecognitionResult(inputToCheck=test_result23, undesiredResult=test_not_in_result23)
            self.assertRecognitionResult(inputToCheck=test_result24, expectResult=test_expect24)
            self.assertRecognitionResult(inputToCheck=test_result25, expectResult=test_expect25)
            self.assertRecognitionResult(inputToCheck=test_result26, expectResult=test_expect26)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00542_NRIR_osr20_feature_LateBinding_Case1_Import_2nonterminal_change0_1(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/LateBinding/Case1/Import_2nonterminal_change0_1

            In this test, first change the parent (importing) grammar and then change the 
            child (imported) grammar. Demonstrates that (dynamic) late binding to different
            grammars causes recognition behavior to change accordingly.

            Expect:
            1) [Test Case]
                a) key1 = 1 which is !> 1 and key2 = 2 which is !> 2. Expect file, computer, monitor recognized.
                b) key1 = 2 which is > 1 and key2 = 3 which is > 2. Expect apple, computer monitor recognized. Expect file not recognized.
                c) change one of the two child grammars. Expect appled recognized. Expect computer not recognized.
        """
        client = gRPCClient()
        test_audio_format = 'pcm'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)

        # Since key1 = 1 which is !> 1 and key2 = 2 which is !> 2, all the three ITEM are allowed
        test_grammar_data1 = 'NRIR_gramA_1.xml?SWI_import.term1=' + client.test_res_url + 'NRIR_gramB_1.xml%3FSWI_vars.key1%3D1;SWI_import.term2=' + client.test_res_url + 'NRIR_gram2_key2.xml%3FSWI_vars.key2%3D2'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams, recogRes=test_recogRes1)
        # ITEM in gram0 - should be recognized
        test_audio11 = "NRIR_file.wav"
        test_expect11 = "<SWI_meaning>{officeitem:file}</SWI_meaning>"
        # ITEM in gram1 - should be recognized
        test_audio12 = "NRIR_computer.wav"
        test_expect12 = "<SWI_meaning>{officeitem:computer}</SWI_meaning>"
        # ITEM in gram2 - should be recognized
        test_audio13 = "NRIR_monitor.wav"
        test_expect13 = "<SWI_meaning>{officeitem:monitor}</SWI_meaning>"
        
        # Since key1 = 2 which is > 1 and key2 = 3 which is > 2
        test_grammar_data2 = 'NRIR_gramA_2.xml?SWI_import.term1=' + client.test_res_url + 'NRIR_gramB_1.xml%3FSWI_vars.key1%3D1;SWI_import.term2=' + client.test_res_url + 'NRIR_gram2_key2.xml%3FSWI_vars.key2%3D2'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams, recogRes=test_recogRes2)
        # File should NOT be recognized
        test_audio21 = "NRIR_file.wav"
        test_not_in_result21 = "<SWI_meaning>{officeitem:file}</SWI_meaning>"
        # Apple should be recognized
        test_audio22 = "NRIR_apple_8kHz.wav"
        test_expect22 = "<SWI_meaning>{officeitem:apple}</SWI_meaning>"
        # Computer should be recognized
        test_audio23 = "NRIR_computer.wav"
        test_expect23 = "<SWI_meaning>{officeitem:computer}</SWI_meaning>"
        # Monitor should be recognized
        test_audio24 = "NRIR_monitor.wav"
        test_expect24 = "<SWI_meaning>{officeitem:monitor}</SWI_meaning>"

        # This time, change one of the two child grammars.
        test_grammar_data3 = 'NRIR_gramA_2.xml?SWI_import.term1=' + client.test_res_url + 'NRIR_gramB_2.xml%3FSWI_vars.key1%3D1;SWI_import.term2=' + client.test_res_url + 'NRIR_gram2_key2.xml%3FSWI_vars.key2%3D2'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri3, mediaType=test_media_type)
        test_recInit3 = client.recognition_init(recogParam=test_recogParams, recogRes=test_recogRes3)
        # Apple should be recognized
        test_audio31 = "NRIR_apple_8kHz.wav"
        test_expect31 = "<SWI_meaning>{officeitem:apple}</SWI_meaning>"
        # Computer should NOT be recognized
        test_audio32 = "NRIR_computer.wav"
        test_not_in_result32 = "<SWI_meaning>{officeitem:computer}</SWI_meaning>"
        #
        try:
            #
            test_result11 = client.qa_nr_recognize_test_func1(audioInput=test_audio11, recInit=test_recInit1)
            time.sleep(1)
            test_result12 = client.qa_nr_recognize_test_func1(audioInput=test_audio12, recInit=test_recInit1)
            time.sleep(1)
            test_result13 = client.qa_nr_recognize_test_func1(audioInput=test_audio13, recInit=test_recInit1)
            time.sleep(1)
            test_result21 = client.qa_nr_recognize_test_func1(audioInput=test_audio21, recInit=test_recInit2)
            time.sleep(1)
            test_result22 = client.qa_nr_recognize_test_func1(audioInput=test_audio22, recInit=test_recInit2)
            time.sleep(1)
            test_result23 = client.qa_nr_recognize_test_func1(audioInput=test_audio23, recInit=test_recInit2)
            time.sleep(1)
            test_result24 = client.qa_nr_recognize_test_func1(audioInput=test_audio24, recInit=test_recInit2)
            time.sleep(1)
            test_result31 = client.qa_nr_recognize_test_func1(audioInput=test_audio31, recInit=test_recInit3)
            time.sleep(1)
            test_result32 = client.qa_nr_recognize_test_func1(audioInput=test_audio32, recInit=test_recInit3)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result11 + "\n"
            msg += "Test recognition result 2: \n" + test_result12 + "\n"
            msg += "Test recognition result 3: \n" + test_result13 + "\n"
            msg += "Test recognition result 4: \n" + test_result21 + "\n"
            msg += "Test recognition result 5: \n" + test_result22 + "\n"
            msg += "Test recognition result 6: \n" + test_result23 + "\n"
            msg += "Test recognition result 7: \n" + test_result24 + "\n"
            msg += "Test recognition result 8: \n" + test_result31 + "\n"
            msg += "Test recognition result 9: \n" + test_result32 + "\n"
            # self.debug(msg)
            # print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result11, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result12, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result13, expectResult=test_expect13)
            #
            self.assertNotRecognitionResult(inputToCheck=test_result21, undesiredResult=test_not_in_result21)
            self.assertRecognitionResult(inputToCheck=test_result22, expectResult=test_expect22)
            self.assertRecognitionResult(inputToCheck=test_result23, expectResult=test_expect23)
            self.assertRecognitionResult(inputToCheck=test_result24, expectResult=test_expect24)
            #
            self.assertRecognitionResult(inputToCheck=test_result31, expectResult=test_expect31)
            self.assertNotRecognitionResult(inputToCheck=test_result32, undesiredResult=test_not_in_result32)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00543_NRIR_osr20_feature_LateBinding_Case1_Import_2nonterminal_change1_0(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/LateBinding/Case1/Import_2nonterminal_change1_0

            Load a grammar that references two non-terminals from two other grammars (using
            late-binding) and recognize against it. Now, change the child (imported) grammar,
            reactivate. Demonstrates that (dynamic) late binding to different imported grammar
            causes recognition behavior to change accordingly. Only the changed, imported
            grammar is reloaded.

            Expect:
            1) [Test Case]
                a) key1 = 1 which is !> 1 and key2 = 2 which is !> 2. Expect file, computer, monitor recognized.
                b) key1 = 2 which is > 1 and key2 = 3 which is > 2. Expect file, orange, monitor recognized. Expect computer not recognized.
        """
        client = gRPCClient()
        test_audio_format = 'pcm'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)

        # Since key1 = 1 which is !> 1 and key2 = 2 which is !> 2, all the three ITEM are allowed
        test_grammar_data1 = 'NRIR_gram0.xml?SWI_import.term1=' + client.test_res_url + 'NRIR_gramB_1.xml%3FSWI_vars.key1%3D1;SWI_import.term2=' + client.test_res_url + 'NRIR_gram2_key2.xml%3FSWI_vars.key2%3D2'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams, recogRes=test_recogRes1)
        # ITEM in gram0 - should be recognized
        test_audio11 = "NRIR_file.wav"
        test_expect11 = "<SWI_meaning>{officeitem:file}</SWI_meaning>"
        # ITEM in gram1 - should be recognized
        test_audio12 = "NRIR_computer.wav"
        test_expect12 = "<SWI_meaning>{officeitem:computer}</SWI_meaning>"
        # ITEM in gram2 - should be recognized
        test_audio13 = "NRIR_monitor.wav"
        test_expect13 = "<SWI_meaning>{officeitem:monitor}</SWI_meaning>"
        
        # Since key1 = 2 which is > 1 and key2 = 3 which is > 2
        test_grammar_data2 = 'NRIR_gram0.xml?SWI_import.term1=' + client.test_res_url + 'NRIR_gramB_2.xml%3FSWI_vars.key1%3D1;SWI_import.term2=' + client.test_res_url + 'NRIR_gram2_key2.xml%3FSWI_vars.key2%3D2'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams, recogRes=test_recogRes2)
        # File should be recognized
        test_audio21 = "NRIR_file.wav"
        test_expect21 = "<SWI_meaning>{officeitem:file}</SWI_meaning>"
        # Computer should NOT be recognized
        test_audio22 = "NRIR_computer.wav"
        test_not_in_result22 = "<SWI_meaning>{officeitem:computer}</SWI_meaning>"
        # Orange should be recognized
        test_audio23 = "NRIR_orange.wav"
        test_expect23 = "<SWI_meaning>{officeitem:orange}</SWI_meaning>"
        # Monitor should be recognized
        test_audio24 = "NRIR_monitor.wav"
        test_expect24 = "<SWI_meaning>{officeitem:monitor}</SWI_meaning>"
        #
        try:
            #
            test_result11 = client.qa_nr_recognize_test_func1(audioInput=test_audio11, recInit=test_recInit1)
            time.sleep(1)
            test_result12 = client.qa_nr_recognize_test_func1(audioInput=test_audio12, recInit=test_recInit1)
            time.sleep(1)
            test_result13 = client.qa_nr_recognize_test_func1(audioInput=test_audio13, recInit=test_recInit1)
            time.sleep(1)
            test_result21 = client.qa_nr_recognize_test_func1(audioInput=test_audio21, recInit=test_recInit2)
            time.sleep(1)
            test_result22 = client.qa_nr_recognize_test_func1(audioInput=test_audio22, recInit=test_recInit2)
            time.sleep(1)
            test_result23 = client.qa_nr_recognize_test_func1(audioInput=test_audio23, recInit=test_recInit2)
            time.sleep(1)
            test_result24 = client.qa_nr_recognize_test_func1(audioInput=test_audio24, recInit=test_recInit2)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result11 + "\n"
            msg += "Test recognition result 2: \n" + test_result12 + "\n"
            msg += "Test recognition result 3: \n" + test_result13 + "\n"
            msg += "Test recognition result 4: \n" + test_result21 + "\n"
            msg += "Test recognition result 6: \n" + test_result22 + "\n"
            msg += "Test recognition result 8: \n" + test_result23 + "\n"
            msg += "Test recognition result 9: \n" + test_result24 + "\n"
            # self.debug(msg)
            # print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result11, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result12, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result13, expectResult=test_expect13)
            #
            self.assertRecognitionResult(inputToCheck=test_result21, expectResult=test_expect21)
            self.assertNotRecognitionResult(inputToCheck=test_result22, undesiredResult=test_not_in_result22)
            self.assertRecognitionResult(inputToCheck=test_result23, expectResult=test_expect23)
            self.assertRecognitionResult(inputToCheck=test_result24, expectResult=test_expect24)            

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00544_NRIR_osr20_feature_LateBinding_Case2_Import_1nonterminal_in_import(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/LateBinding/Case2/Import_1nonterminal_in_import

            Load a grammar that dynamically imports a non-terminal from another grammar.
            This imported grammar itself imports a non-terminal from yet another grammar.
            Activate and recognize against this composite grammar. Vocabulary items from
            the separate grammars should be recognized in the composite grammar.
            Demonstrates the capability to nest references to dynamically bound grammars in
            the URL (as well as pass in name/value variable assignments at each level)

            Expect:
            1) [Test Case]
                a) key1 = 1 which is !> 1 and key2 = 2 which is !> 2. Expect file, computer, monitor recognized.
                b) key1 = 2 which is > 1 and key2 = 3 which is > 2. Expect file recognized. Expect computer, monitor not recognized.
                c) key1 = 1 which is !> 1 and key2 = 3 which is > 2. Expect file, computer recognized. Expect monitor not recognized.

            parameters ignored:
            - SWIrecAcousticStateReset REC
            - SWIrecRecognizerSetParameter REC swirec_load_adjusted_speedvsaccuracy idle
        """
        client = gRPCClient()
        test_audio_format = 'pcm'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)

        # Since key1 = 1 which is !> 1 and key2 = 2 which is !> 2, all the three ITEM are allowed
        test_grammar_data1 = 'NRIR_gram0a.xml?SWI_import.term1=' + client.test_res_url + 'NRIR_gram1a_key1.xml%3FSWI_vars.key1%3D1%3BSWI_import.term2%3D' + client.test_res_url + 'NRIR_gram2a_key2.xml%253FSWI_vars.key2%253D2'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams, recogRes=test_recogRes1)
        # ITEM in gram0a - should be recognized
        test_audio11 = "NRIR_file.wav"
        test_expect11 = "<SWI_meaning>{officeitem:file}</SWI_meaning>"
        # ITEM in gram1 - should be recognized
        test_audio12 = "NRIR_computer.wav"
        test_expect12 = "<SWI_meaning>{officeitem:computer}</SWI_meaning>"
        # ITEM in gram2 - should be recognized
        test_audio13 = "NRIR_monitor.wav"
        test_expect13 = "<SWI_meaning>{officeitem:monitor}</SWI_meaning>"
        
        # Since key1 = 2 which is > 1 and key2 = 3 which is > 2, disallowed
        test_grammar_data2 = 'NRIR_gram0a.xml?SWI_import.term1=' + client.test_res_url + 'NRIR_gram1a_key1.xml%3FSWI_vars.key1%3D2%3BSWI_import.term2%3D' + client.test_res_url + 'NRIR_gram2a_key2.xml%253FSWI_vars.key2%253D3'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams, recogRes=test_recogRes2)
        # ITEM in  gram0a - should be recognized
        test_audio21 = "NRIR_file.wav"
        test_expect21 = "<SWI_meaning>{officeitem:file}</SWI_meaning>"
        # ITEM in  gram1 - should be disallowed
        test_audio22 = "NRIR_computer.wav"
        #test_expect22 = "SWIrec_STATUS_NO_MATCH"
        #test_expect22 =  "<result>.*nomatch.*/result>"
        test_expect22 = "NO_MATCH"
        # ITEM in  gram2 - should be disallowed
        test_audio23 = "NRIR_monitor.wav"
        #test_expect23 = "SWIrec_STATUS_NO_MATCH"
        test_expect23 = "NO_MATCH"
        #test_expect23 =  "<result>.*nomatch.*/result>"

        # Since key1 = 1 which is !> 1 and key2 = 3 which is > 2
        test_grammar_data3 = 'NRIR_gram0a.xml?SWI_import.term1=' + client.test_res_url + 'NRIR_gram1a_key1.xml%3FSWI_vars.key1%3D1%3BSWI_import.term2%3D' + client.test_res_url + 'NRIR_gram2a_key2.xml%253FSWI_vars.key2%253D3'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri3, mediaType=test_media_type)
        test_recInit3 = client.recognition_init(recogParam=test_recogParams, recogRes=test_recogRes3)
        # ITEM in  gram0a - should be recognized
        test_audio31 = "NRIR_file.wav"
        test_expect31 = "<SWI_meaning>{officeitem:file}</SWI_meaning>"
        # ITEM in  gram1 - should be recognized
        test_audio32 = "NRIR_computer.wav"
        test_expect32 = "<SWI_meaning>{officeitem:computer}</SWI_meaning>"
        # ITEM in  gram2 - should be disallowed
        test_audio33 = "NRIR_monitor.wav"
        #test_expect33 = "SWIrec_STATUS_NO_MATCH"
        test_expect33 = "NO_MATCH"
        #test_expect33 =  "<result>.*nomatch.*/result>"
        #
        try:
            #
            test_result11 = client.qa_nr_recognize_test_func1(audioInput=test_audio11, recInit=test_recInit1)
            time.sleep(1)
            test_result12 = client.qa_nr_recognize_test_func1(audioInput=test_audio12, recInit=test_recInit1)
            time.sleep(1)
            test_result13 = client.qa_nr_recognize_test_func1(audioInput=test_audio13, recInit=test_recInit1)
            time.sleep(1)
            test_result21 = client.qa_nr_recognize_test_func1(audioInput=test_audio21, recInit=test_recInit2)
            time.sleep(1)
            test_result22 = client.qa_nr_recognize_test_func1(audioInput=test_audio22, recInit=test_recInit2)
            time.sleep(1)
            test_result23 = client.qa_nr_recognize_test_func1(audioInput=test_audio23, recInit=test_recInit2)
            time.sleep(1)
            test_result31 = client.qa_nr_recognize_test_func1(audioInput=test_audio31, recInit=test_recInit3)
            time.sleep(1)
            test_result32 = client.qa_nr_recognize_test_func1(audioInput=test_audio32, recInit=test_recInit3)
            time.sleep(1)
            test_result33 = client.qa_nr_recognize_test_func1(audioInput=test_audio33, recInit=test_recInit3)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result11 + "\n"
            msg += "Test recognition result 2: \n" + test_result12 + "\n"
            msg += "Test recognition result 3: \n" + test_result13 + "\n"
            msg += "Test recognition result 4: \n" + test_result21 + "\n"
            msg += "Test recognition result 5: \n" + test_result22 + "\n"
            msg += "Test recognition result 6: \n" + test_result23 + "\n"
            msg += "Test recognition result 7: \n" + test_result31 + "\n"
            msg += "Test recognition result 8: \n" + test_result32 + "\n"
            msg += "Test recognition result 9: \n" + test_result33 + "\n"
            # self.debug(msg)
            # print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result11, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result12, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result13, expectResult=test_expect13)
            #
            self.assertRecognitionResult(inputToCheck=test_result21, expectResult=test_expect21)
            self.assertRecognitionResult(inputToCheck=test_result22, expectResult=test_expect22)
            self.assertRecognitionResult(inputToCheck=test_result23, expectResult=test_expect23)
            #
            self.assertRecognitionResult(inputToCheck=test_result31, expectResult=test_expect31)
            self.assertRecognitionResult(inputToCheck=test_result32, expectResult=test_expect32)
            self.assertRecognitionResult(inputToCheck=test_result33, expectResult=test_expect33)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00545_NRIR_osr20_feature_LateBinding_Case2_Import_1nonterminal_in_import_change0(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/LateBinding/Case2/Import_1nonterminal_in_import_change0

        This test is similar to Import_1nonterminal_in_import but, after the initial
        activation and recognition, the top-most grammar is deliberately changed and 
        the whole lot is reactivated.  Only the top-most (changed) grammar should be
        reloaded. Recognize against this new composite grammar to demonstrate that the
        changes are in effect. Finally, reactivate the composite grammar, changing only
        the value of some control variables. This demonstrates that name/value pairs can
        be passed in at each level of dynamic binding.

        Expect:
            1) [Test Case]
                a) key1 = 1 which is !> 1 and key2 = 2 which is !> 2. Expect file recognized. Expect computer, monitor not recognized.
                b) key1 = 2 which is > 1 and key2 = 3 which is > 2. Expect apple recognized. Expect file, computer, monitor not recognized.
                c) key1 = 1 which is !> 1 and key2 = 3 which is > 2. Expect apple, computer recognized. Expect monitor not recognized.

        parameters ignored:
        - SWIrecAcousticStateReset REC
        - SWIrecRecognizerSetParameter REC swirec_load_adjusted_speedvsaccuracy idle
        """
        client = gRPCClient()
        test_audio_format = 'pcm'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)

        # Since key1 = 1 which is !> 1 and key2 = 2 which is !> 2, all the three ITEM are allowed
        test_grammar_data1 = 'NRIR_gramAa_1.xml?SWI_import.term1=' + client.test_res_url + 'NRIR_gram1a_key1.xml%3FSWI_vars.key1%3D2%3BSWI_import.term2%3D' + client.test_res_url + 'NRIR_gram2a_key2.xml%253FSWI_vars.key2%253D3'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams, recogRes=test_recogRes1)
        # ITEM in gram0a - should be recognized
        test_audio11 = "NRIR_file.wav"
        test_expect11 = "<SWI_meaning>{officeitem:file}</SWI_meaning>"
        # ITEM in gram1 - should not be recognized
        test_audio12 = "NRIR_computer.wav"
        test_not_in_result12 = "<SWI_meaning>{officeitem:computer}</SWI_meaning>"
        # ITEM in gram2 - should not be recognized
        test_audio13 = "NRIR_monitor.wav"
        test_not_in_result13 = "<SWI_meaning>{officeitem:monitor}</SWI_meaning>"
        
        # Since key1 = 2 which is > 1 and key2 = 3 which is > 2, disallowed
        test_grammar_data2 = 'NRIR_gramAa_2.xml?SWI_import.term1=' + client.test_res_url + 'NRIR_gram1a_key1.xml%3FSWI_vars.key1%3D2%3BSWI_import.term2%3D' + client.test_res_url + 'NRIR_gram2a_key2.xml%253FSWI_vars.key2%253D3'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams, recogRes=test_recogRes2)
        # file should NOT be recognized
        test_audio21 = "NRIR_file.wav"
        test_not_in_result21 = "<SWI_meaning>{officeitem:file}</SWI_meaning>"
        # apple should be recognized
        test_audio22 = "NRIR_apple_8kHz.wav"
        test_expect22 = "<SWI_meaning>{officeitem:apple}</SWI_meaning>"
        # ITEM in gram1 - should be disallowed
        test_audio23 = "NRIR_computer.wav"
        #test_expect23 = "SWIrec_STATUS_NO_MATCH"
        test_expect23 = "NO_MATCH"
        #test_expect23 =  "<result>.*nomatch.*/result>"
        # ITEM in gram2 - should be disallowed
        test_audio24 = "NRIR_monitor.wav"
        #test_expect24 = "SWIrec_STATUS_NO_MATCH"
        test_expect24 = "NO_MATCH"
        #test_expect24 =  "<result>.*nomatch.*/result>"

        # Since key1 = 1 which is !> 1 and key2 = 3 which is > 2
        test_grammar_data3 = 'NRIR_gramAa_2.xml?SWI_import.term1=' + client.test_res_url + 'NRIR_gram1a_key1.xml%3FSWI_vars.key1%3D1%3BSWI_import.term2%3D' + client.test_res_url + 'NRIR_gram2a_key2.xml%253FSWI_vars.key2%253D3'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri3, mediaType=test_media_type)
        test_recInit3 = client.recognition_init(recogParam=test_recogParams, recogRes=test_recogRes3)
        # ITEM in  gram0a - should be recognized
        test_audio31 = "NRIR_apple_8kHz.wav"
        test_expect31 = "<SWI_meaning>{officeitem:apple}</SWI_meaning>"
        # ITEM in  gram1 - should be recognized
        test_audio32 = "NRIR_computer.wav"
        test_expect32 = "<SWI_meaning>{officeitem:computer}</SWI_meaning>"
        # ITEM in  gram2 - should be disallowed
        test_audio33 = "NRIR_monitor.wav"
        #test_expect33 = "SWIrec_STATUS_NO_MATCH"
        #test_expect33 =  "<result>.*nomatch.*/result>"
        test_expect33 = "NO_MATCH"
        #
        try:
            #
            test_result11 = client.qa_nr_recognize_test_func1(audioInput=test_audio11, recInit=test_recInit1)
            time.sleep(1)
            test_result12 = client.qa_nr_recognize_test_func1(audioInput=test_audio12, recInit=test_recInit1)
            time.sleep(1)
            test_result13 = client.qa_nr_recognize_test_func1(audioInput=test_audio13, recInit=test_recInit1)
            time.sleep(1)
            test_result21 = client.qa_nr_recognize_test_func1(audioInput=test_audio21, recInit=test_recInit2)
            time.sleep(1)
            test_result22 = client.qa_nr_recognize_test_func1(audioInput=test_audio22, recInit=test_recInit2)
            time.sleep(1)
            test_result23 = client.qa_nr_recognize_test_func1(audioInput=test_audio23, recInit=test_recInit2)
            time.sleep(1)
            test_result24 = client.qa_nr_recognize_test_func1(audioInput=test_audio24, recInit=test_recInit2)
            time.sleep(1)
            test_result31 = client.qa_nr_recognize_test_func1(audioInput=test_audio31, recInit=test_recInit3)
            time.sleep(1)
            test_result32 = client.qa_nr_recognize_test_func1(audioInput=test_audio32, recInit=test_recInit3)
            time.sleep(1)
            test_result33 = client.qa_nr_recognize_test_func1(audioInput=test_audio33, recInit=test_recInit3)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result11 + "\n"
            msg += "Test recognition result 2: \n" + test_result12 + "\n"
            msg += "Test recognition result 3: \n" + test_result13 + "\n"
            msg += "Test recognition result 4: \n" + test_result21 + "\n"
            msg += "Test recognition result 5: \n" + test_result22 + "\n"
            msg += "Test recognition result 6: \n" + test_result23 + "\n"
            msg += "Test recognition result 7: \n" + test_result24 + "\n"
            msg += "Test recognition result 8: \n" + test_result31 + "\n"
            msg += "Test recognition result 9: \n" + test_result32 + "\n"
            msg += "Test recognition result 10: \n" + test_result33 + "\n"
            # self.debug(msg)
            # print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result11, expectResult=test_expect11)
            self.assertNotRecognitionResult(inputToCheck=test_result12, undesiredResult=test_not_in_result12)
            self.assertNotRecognitionResult(inputToCheck=test_result13, undesiredResult=test_not_in_result13)
            #
            self.assertNotRecognitionResult(inputToCheck=test_result21, undesiredResult=test_not_in_result21)
            self.assertRecognitionResult(inputToCheck=test_result22, expectResult=test_expect22)
            self.assertRecognitionResult(inputToCheck=test_result23, expectResult=test_expect23)
            self.assertRecognitionResult(inputToCheck=test_result24, expectResult=test_expect24)
            #
            self.assertRecognitionResult(inputToCheck=test_result31, expectResult=test_expect31)
            self.assertRecognitionResult(inputToCheck=test_result32, expectResult=test_expect32)
            self.assertRecognitionResult(inputToCheck=test_result33, expectResult=test_expect33)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00546_NRIR_osr20_feature_LateBinding_Case2_Import_1nonterminal_in_import_change0_1_2(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/LateBinding/Case2/Import_1nonterminal_in_import_change0_1_2

        This test is similar to Import_1nonterminal_in_import_change0 except that first
        the top-most grammar is modified, then the second level imported grammar is 
        modified, and finally the lowest level imported grammar is modified. At each
        stage, only the modified grammar should be reloaded. Demonstrates the
        independence of the grammars when using the dynamic (late binding) mechanism.

        Expect:
            1) [Test Case]
                a) key1 = 1 which is !> 1 and key2 = 2 which is !> 2. Expect file recognized. Expect computer, monitor not recognized.
                b) Expect apple, computer, monitor recognized. Expect file not recognized.
                c) key1 = 1 which is !> 1 and key2 = 3 which is > 2. Expect apple, mango recognized. Expect file, orange, computer, monitor not recognized.

        parameters ignored:
        - SWIrecAcousticStateReset REC
        - SWIrecRecognizerSetParameter REC swirec_load_adjusted_speedvsaccuracy idle
        """
        client = gRPCClient()
        test_audio_format = 'pcm'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)

        # Since key1 = 1 which is !> 1 and key2 = 2 which is !> 2, all the three ITEM, are allowed
        test_grammar_data1 = 'NRIR_gramAa_1.xml?SWI_import.term1=' + client.test_res_url + 'NRIR_gramBa_1.xml%3FSWI_vars.key1%3D1%3BSWI_import.term2%3D' + client.test_res_url + 'NRIR_gramCa_1.xml%253FSWI_vars.key2%253D2'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recInit1 = client.recognition_init(recogParam=test_recogParams, recogRes=test_recogRes1)
        # ITEM in gram0a - should be recognized
        test_audio11 = "NRIR_file.wav"
        test_expect11 = "<SWI_literal>file</SWI_literal>"
        # ITEM in gram1 - should not be recognized
        test_audio12 = "NRIR_computer.wav"
        test_expect12 = "<SWI_literal>computer</SWI_literal>"
        # ITEM in gram2 - should not be recognized
        test_audio13 = "NRIR_monitor.wav"
        test_expect13 = "<SWI_literal>monitor</SWI_literal>"
        
        #
        test_grammar_data2 = 'NRIR_gramAa_2.xml?SWI_import.term1=' + client.test_res_url + 'NRIR_gramBa_1.xml%3FSWI_vars.key1%3D1%3BSWI_import.term2%3D' + client.test_res_url + 'NRIR_gramCa_1.xml%253FSWI_vars.key2%253D2'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type)
        test_recInit2 = client.recognition_init(recogParam=test_recogParams, recogRes=test_recogRes2)
        # file should NOT be recognized
        test_audio21 = "NRIR_file.wav"
        test_not_in_result21 = "<SWI_literal>file</SWI_literal>"
        # apple should be recognized
        test_audio22 = "NRIR_apple_8kHz.wav"
        test_expect22 = "<SWI_literal>apple</SWI_literal>"
        # ITEM in gram1
        test_audio23 = "NRIR_computer.wav"
        test_expect23 = "<SWI_literal>computer</SWI_literal>"
        # ITEM in gram2
        test_audio24 = "NRIR_monitor.wav"
        test_expect24 = "<SWI_literal>monitor</SWI_literal>"

        # Since key1 = 1 which is !> 1 and key2 = 2 which is !> 2
        test_grammar_data3 = 'NRIR_gramAa_2.xml?SWI_import.term1=' + client.test_res_url + 'NRIR_gramBa_2.xml%3FSWI_vars.key1%3D1%3BSWI_import.term2%3D' + client.test_res_url + 'NRIR_gramCa_1.xml%253FSWI_vars.key2%253D2'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri3, mediaType=test_media_type)
        test_recInit3 = client.recognition_init(recogParam=test_recogParams, recogRes=test_recogRes3)
        # file should NOT be recognized
        test_audio31 = "NRIR_file.wav"
        test_not_in_result31 = "<SWI_literal>file</SWI_literal>"
        # apple should be recognized
        test_audio32 = "NRIR_apple_8kHz.wav"
        test_expect32 = "<SWI_literal>apple</SWI_literal>"
        # computer should NOT be recognized
        test_audio33 = "NRIR_computer.wav"
        test_not_in_result33 = "<SWI_literal>computer</SWI_literal>"
        # orange should be recognized (new middle grammar)
        test_audio34 = "NRIR_orange.wav"
        test_expect34 = "<SWI_literal>orange</SWI_literal>"
        # ITEM in gram2
        test_audio35 = "NRIR_monitor.wav"
        test_expect35 = "<SWI_literal>monitor</SWI_literal>"

        # Since key1 = 2 which is > 1 and key2 = 3 which is > 2
        test_grammar_data4 = 'NRIR_gramAa_2.xml?SWI_import.term1=' + client.test_res_url + 'NRIR_gramBa_2.xml%3FSWI_vars.key1%3D2%3BSWI_import.term2%3D' + client.test_res_url + 'NRIR_gramCa_2.xml%253FSWI_vars.key2%253D2'
        test_grammar_uri4 = client.test_res_url + test_grammar_data4
        test_recogRes4 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri4, mediaType=test_media_type)
        test_recInit4 = client.recognition_init(recogParam=test_recogParams, recogRes=test_recogRes4)
        # file should NOT be recognized
        test_audio41 = "NRIR_file.wav"
        test_not_in_result41 = "<SWI_literal>file</SWI_literal>"
        # apple should be recognized
        test_audio42 = "NRIR_apple_8kHz.wav"
        test_expect42 = "<SWI_literal>apple</SWI_literal>"
        # computer should NOT be recognized
        test_audio43 = "NRIR_computer.wav"
        test_not_in_result43 = "<SWI_literal>computer</SWI_literal>"
        # orange should be disallowed
        test_audio44 = "NRIR_orange.wav"
        test_not_in_result44 = "<SWI_literal>orange</SWI_literal>"
        # monitor should not be recognized (old bottom grammar)
        test_audio45 = "NRIR_monitor.wav"
        test_not_in_result45 = "<SWI_literal>monitor</SWI_literal>"
        # mango should be recognized (new bottom grammar)
        test_audio46 = "NRIR_mango.wav"
        test_expect46 = "<SWI_literal>mango</SWI_literal>"
        #
        try:
            #
            test_result11 = client.qa_nr_recognize_test_func1(audioInput=test_audio11, recInit=test_recInit1)
            time.sleep(1)
            test_result12 = client.qa_nr_recognize_test_func1(audioInput=test_audio12, recInit=test_recInit1)
            time.sleep(1)
            test_result13 = client.qa_nr_recognize_test_func1(audioInput=test_audio13, recInit=test_recInit1)
            time.sleep(1)
            test_result21 = client.qa_nr_recognize_test_func1(audioInput=test_audio21, recInit=test_recInit2)
            time.sleep(1)
            test_result22 = client.qa_nr_recognize_test_func1(audioInput=test_audio22, recInit=test_recInit2)
            time.sleep(1)
            test_result23 = client.qa_nr_recognize_test_func1(audioInput=test_audio23, recInit=test_recInit2)
            time.sleep(1)
            test_result24 = client.qa_nr_recognize_test_func1(audioInput=test_audio24, recInit=test_recInit2)
            time.sleep(1)
            test_result31 = client.qa_nr_recognize_test_func1(audioInput=test_audio31, recInit=test_recInit3)
            time.sleep(1)
            test_result32 = client.qa_nr_recognize_test_func1(audioInput=test_audio32, recInit=test_recInit3)
            time.sleep(1)
            test_result33 = client.qa_nr_recognize_test_func1(audioInput=test_audio33, recInit=test_recInit3)
            time.sleep(1)
            test_result34 = client.qa_nr_recognize_test_func1(audioInput=test_audio34, recInit=test_recInit3)
            time.sleep(1)
            test_result35 = client.qa_nr_recognize_test_func1(audioInput=test_audio35, recInit=test_recInit3)
            time.sleep(1)
            #
            test_result41 = client.qa_nr_recognize_test_func1(audioInput=test_audio41, recInit=test_recInit4)
            time.sleep(1)
            test_result42 = client.qa_nr_recognize_test_func1(audioInput=test_audio42, recInit=test_recInit4)
            time.sleep(1)
            test_result43 = client.qa_nr_recognize_test_func1(audioInput=test_audio43, recInit=test_recInit4)
            time.sleep(1)
            test_result44 = client.qa_nr_recognize_test_func1(audioInput=test_audio44, recInit=test_recInit4)
            time.sleep(1)
            test_result45 = client.qa_nr_recognize_test_func1(audioInput=test_audio45, recInit=test_recInit4)
            time.sleep(1)
            test_result46 = client.qa_nr_recognize_test_func1(audioInput=test_audio46, recInit=test_recInit4)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result11 + "\n"
            msg += "Test recognition result 2: \n" + test_result12 + "\n"
            msg += "Test recognition result 3: \n" + test_result13 + "\n"
            msg += "Test recognition result 4: \n" + test_result21 + "\n"
            msg += "Test recognition result 5: \n" + test_result22 + "\n"
            msg += "Test recognition result 6: \n" + test_result23 + "\n"
            msg += "Test recognition result 7: \n" + test_result24 + "\n"
            msg += "Test recognition result 8: \n" + test_result31 + "\n"
            msg += "Test recognition result 9: \n" + test_result32 + "\n"
            msg += "Test recognition result 10: \n" + test_result33 + "\n"
            msg += "Test recognition result 11: \n" + test_result34 + "\n"
            msg += "Test recognition result 12: \n" + test_result35 + "\n"
            msg += "Test recognition result 13: \n" + test_result41 + "\n"
            msg += "Test recognition result 14: \n" + test_result42 + "\n"
            msg += "Test recognition result 15: \n" + test_result43 + "\n"
            msg += "Test recognition result 16: \n" + test_result44 + "\n"
            msg += "Test recognition result 17: \n" + test_result45 + "\n"
            msg += "Test recognition result 18: \n" + test_result46 + "\n"
            # self.debug(msg)
            # print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result11, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result12, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result13, expectResult=test_expect13)
            #
            self.assertNotRecognitionResult(inputToCheck=test_result21, undesiredResult=test_not_in_result21)
            self.assertRecognitionResult(inputToCheck=test_result22, expectResult=test_expect22)
            self.assertRecognitionResult(inputToCheck=test_result23, expectResult=test_expect23)
            self.assertRecognitionResult(inputToCheck=test_result24, expectResult=test_expect24)
            #
            self.assertNotRecognitionResult(inputToCheck=test_result31, undesiredResult=test_not_in_result31)
            self.assertRecognitionResult(inputToCheck=test_result32, expectResult=test_expect32)
            self.assertNotRecognitionResult(inputToCheck=test_result33, undesiredResult=test_not_in_result33)
            self.assertRecognitionResult(inputToCheck=test_result34, expectResult=test_expect34)
            self.assertRecognitionResult(inputToCheck=test_result35, expectResult=test_expect35)
            #
            self.assertNotRecognitionResult(inputToCheck=test_result41, undesiredResult=test_not_in_result41)
            self.assertRecognitionResult(inputToCheck=test_result42, expectResult=test_expect42)
            self.assertNotRecognitionResult(inputToCheck=test_result43, undesiredResult=test_not_in_result43)
            self.assertNotRecognitionResult(inputToCheck=test_result44, undesiredResult=test_not_in_result44)
            self.assertNotRecognitionResult(inputToCheck=test_result45, undesiredResult=test_not_in_result45)
            self.assertRecognitionResult(inputToCheck=test_result46, expectResult=test_expect46)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00547_NRIR_osr_quantum_feature_param_gram_precedence_param_gram_precedence_multi_override_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/param_gram_precedence/param_gram_precedence_multi_override_PERL

        Parameter Grammar Precedence attribute test.
        Note: NRIR test case uses override attribute to parameter grammar, but it is NOT SUPPORTED in NRC.
        Expect:
        1) [Test case]
            a) 5=SWI_meaning, 7=SWI_spoken; should only be SWI_spoken 
            b) 5=SWI_meaning, 7=SWI_spoken, 9=SWI_literal; should yield only SWI_literal
        """
        client = gRPCClient()
        
        test_audio = "NRIR_12345.wav"
        test_audio_format = 'pcm'
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_digits.xml'
        test_media_type1 = 'srgsxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
       
        # Load 5=SWI_meaning
        test_grammar_type2 = 'uri_grammar'
        test_grammar_data2 = 'NRIR_prec_5.xml'
        test_media_type2 = 'xswiparameter'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        # Load 7=SWI_spoken
        test_grammar_type3 = 'uri_grammar'
        test_grammar_data3 = 'NRIR_prec_7.xml'
        test_media_type3 = 'xswiparameter'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_uri3, mediaType=test_media_type3)
        # Load 9=SWI_literal
        test_grammar_type5 = 'uri_grammar'
        test_grammar_data5 = 'NRIR_prec_9.xml'
        test_media_type5 = 'xswiparameter'
        test_grammar_uri5 = client.test_res_url + test_grammar_data5
        test_recogRes5 = client.recognition_resource(grammarType=test_grammar_type5, grammarData=test_grammar_uri5, mediaType=test_media_type5)
        
        # 1) a)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes_1 = [test_recogRes1, test_recogRes2, test_recogRes3]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_1) 
        test_expect1 = "SWI_spoken"
        # 1) b)
        test_recogRes_2 = [test_recogRes1, test_recogRes2, test_recogRes3, test_recogRes5] 
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_2)
        test_expect2 = "SWI_literal"
        #
        try:
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
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00548_NRIR_osr_quantum_feature_param_gram_precedence_param_gram_precedence_override_PERL_1(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/param_gram_precedence/param_gram_precedence_override_PERL_1
    
        Parameter Grammar Precedence validation.
        Expect:
        1) [Test Case]:
            a) SWI_grammarName has prec=1, SWI_spoken has prec=8. Override set to 1. Expect SWI_spoken.
        
        parameters ignored:
            - SWIrecAcousticStateReset theRec
        """
        client = gRPCClient()

        test_audio = "NRIR_12345.wav"
        test_audio_format = 'pcm'
        test_expect1 = "SWI_spoken"
        #
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_digits.xml'
        test_media_type1 = 'srgsxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        #
        test_grammar_type2 = 'uri_grammar'
        test_grammar_data2 = 'NRIR_prec_8_override_1.xml'
        test_media_type2 = 'xswiparameter'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        #
        test_grammar_type3 = 'uri_grammar'
        test_grammar_data3 = 'NRIR_parameter_grammar_swirec_extra_nbest_keys_SWI_grammarName.grxml'
        test_media_type3 = 'xswiparameter'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_uri3, mediaType=test_media_type3)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes_1 = [test_recogRes1, test_recogRes2, test_recogRes3]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_1) 
        #
        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            #
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00549_NRIR_osr_quantum_feature_param_gram_precedence_param_gram_precedence_override_PERL_true(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/param_gram_precedence/param_gram_precedence_override_PERL_true
    
        Parameter Grammar Precedence validation.
        Expect:
        1) [Test Case]:
            a) SWI_grammarName has prec=1, SWI_spoken has prec=8. Override set to true. Expect SWI_spoken.
        """
        client = gRPCClient()

        test_audio = "NRIR_12345.wav"
        test_audio_format = 'pcm'
        test_expect1 = "SWI_spoken"
        #
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_digits.xml'
        test_media_type1 = 'srgsxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        #
        test_grammar_type2 = 'uri_grammar'
        test_grammar_data2 = 'NRIR_true_override.xml'
        test_media_type2 = 'xswiparameter'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        #
        test_grammar_type3 = 'uri_grammar'
        test_grammar_data3 = 'NRIR_parameter_grammar_swirec_extra_nbest_keys_SWI_grammarName.grxml'
        test_media_type3 = 'xswiparameter'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_uri3, mediaType=test_media_type3)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes_1 = [test_recogRes1, test_recogRes2, test_recogRes3]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_1) 
        #
        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            #
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00550_NRIR_osr_quantum_feature_param_gram_precedence_param_gram_precedence_override_PERL_TRUE_UPPER(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/param_gram_precedence/param_gram_precedence_override_PERL_TRUE_UPPER
    
        Parameter Grammar Precedence validation.
        Expect:
        1) [Test Case]:
            a) SWI_grammarName has prec=1, SWI_spoken has prec=8. Override set to TRUE. Expect SWI_spoken.
        """
        client = gRPCClient()

        test_audio = "NRIR_12345.wav"
        test_audio_format = 'pcm'
        test_expect1 = "SWI_spoken"
        #
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_digits.xml'
        test_media_type1 = 'srgsxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        #
        test_grammar_type2 = 'uri_grammar'
        test_grammar_data2 = 'NRIR_TRUE_UPPER_override.xml'
        test_media_type2 = 'xswiparameter'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        #
        test_grammar_type3 = 'uri_grammar'
        test_grammar_data3 = 'NRIR_parameter_grammar_swirec_extra_nbest_keys_SWI_grammarName.grxml'
        test_media_type3 = 'xswiparameter'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3

        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_uri3, mediaType=test_media_type3)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes_1 = [test_recogRes1, test_recogRes2, test_recogRes3]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_1) 
        #
        try:
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            #
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00551_NRIR_osr_quantum_feature_param_gram_precedence_param_gram_precedence_range_override_PERL(self):
        """
        NR IR Converted testcases:
            ./osr_quantum_feature/param_gram_precedence/param_gram_precedence_range_override_PERL
    
        Parameter Grammar Precedence. The Following test will be used to ensure that range for the
        precendece attribute is 1-10. (it will test -1 and 12 because 0-11 can be used in training)

        Expect:
        1) [Test Case]
            a) precedence set to -1 --> Fails to load
            b) precedence set to 12 --> Fails to load
            c) precedence set to 7  --> Works

        - swirec_extra_nbest_keys "SWI_grammarName" set in a parameter grammar
        """
        client = gRPCClient()

        test_audio = "NRIR_12345.wav"
        test_audio_format = 'pcm'
        #
        test_grammar_type = 'uri_grammar'
        test_grammar_data = 'NRIR_digits.xml'
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar_data
        #
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_prec_-1.xml'
        test_media_type1 = 'xswiparameter'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        #
        test_grammar_type2 = 'uri_grammar'
        test_grammar_data2 = 'NRIR_prec_12.xml'
        test_media_type2 = 'xswiparameter'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        #
        test_grammar_type3 = 'uri_grammar'
        test_grammar_data3 = 'NRIR_parameter_grammar_swirec_extra_nbest_keys_SWI_grammarName.grxml'
        test_media_type3 = 'xswiparameter'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        #
        test_grammar_type4 = 'uri_grammar'
        test_grammar_data4 = 'NRIR_prec_7.xml'
        test_media_type4 = 'xswiparameter'
        test_grammar_uri4 = client.test_res_url + test_grammar_data4

        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_uri3, mediaType=test_media_type3)
        test_recogRes4 = client.recognition_resource(grammarType=test_grammar_type4, grammarData=test_grammar_uri4, mediaType=test_media_type4)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        
        # precedence set to -1 --> Fails to load
        test_recogRes_1 = [test_recogRes, test_recogRes1, test_recogRes3]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_1)
        test_expect11 = "code: 400"
        test_expect12 = "message: \"Bad Request\""
        test_expect13 = "details: \"Failed to load RecognitionResource"

        # precedence set to 12 --> Fails to load
        test_recogRes_2 = [test_recogRes, test_recogRes2, test_recogRes3]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_2)
        test_expect21 = "code: 400"
        test_expect22 = "message: \"Bad Request\""
        test_expect23 = "details: \"Failed to load RecognitionResource"

        # precedence set to 7 --> Works
        test_recogRes_3 = [test_recogRes, test_recogRes4, test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_3)
        test_expect3 = "SWI_spoken"
        #
        try:
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
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect13)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect21)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect22)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect23)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            time.sleep(20)

    def test00552_NRIR_proton_feature_parameter_test_swirec_lmweight_import_PERL(self):
        """
        NR IR Converted testcases:
            ./proton_feature/parameter_test/swirec_lmweight_import_PERL
    
        This test verifies that the parameter swirec_lmweight of a parent grammar will override a value set in the imported

        If the result with the lower value for lmweight does not contain the higher weighted
        entry but the higher weighted result does, then we can assume the parameter had the
        desired effect
        
        Expect:
        1) [Test Case]
            a) Test with lower value for lmweight=0.01. Expect lower weighted entry <item weight="0.1">Greg Hartman</item>.
            b) Test with high value for lmweight=1000. Expect higher weighted entry <item weight="0.9">Greg Hardiman</item>.
        """
        client = gRPCClient()

        test_audio = "NRIR_SS_MapQuest000109_utt000.wav"
        test_audio_format = 'pcm'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        # 1) a)
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_item_weight_lmweight_small.xml'
        test_media_type1 = 'srgsxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_expect1 = "Greg Hartman"
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogRes_1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_1) 
        # 1) b)
        test_grammar_type2 = 'uri_grammar'
        test_grammar_data2 = 'NRIR_lmweight1000_import_item_weight_.xml'
        test_media_type2 = 'srgsxml'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_expect2 = "Greg Hardiman"
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        test_recogRes_2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_2) 
        #
        try:
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
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00553_NRIR_osr20_feature_Grammar_SWI_vars_delta_score_PERL(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/Grammar/SWI_vars/delta_score_PERL

        In this test we use SWI_var to dynamically apply SWI_scoreDelta to certain items in a vocabulary test with real audio.
        We expect the accuracy to degrade with list2 when score adjustment is activated in the grammar.
        Expect:
        1) [Test Case]
            a) list2 with no score adjustment. Expect SWI_scoreDelta 0
            b) list2 with score adjustment. Expect SWI_scoreDelta -2000 due to lower_scores parameter set to true.
        """
        client = gRPCClient()

        test_grammar_type = 'uri_grammar'
        test_grammar_data = 'NRIR_parameter_grammar_swirec_extra_nbest_keys_SWI_scoreDelta.grxml'
        test_media_type = 'xswiparameter'
        test_grammar_uri = client.test_res_url + test_grammar_data
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)

        # step1: list2 with no score adjustment.
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'NRIR_delta_conf_.xml'
        test_media_type1 = 'srgsxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogRes1 = [test_recogRes1, test_recogRes]
        
        # step2: list2 with score adjustment.
        test_grammar_type2 = 'uri_grammar'
        test_grammar_data2 = 'NRIR_delta_conf_.xml?SWI_vars.lower_scores=true'
        test_media_type2 = 'srgsxml'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        test_recogRes2 = [test_recogRes2, test_recogRes]

        # Test audios for test with and w/o adjustments
        test_audio1 = "NRIR_Charlotte_NothCarolina.wav"
        test_audio_format1 = 'pcm'
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes2)
        test_expect11 = "<SWI_scoreDelta>0</SWI_scoreDelta>"
        test_expect12 = "<SWI_scoreDelta>-2000</SWI_scoreDelta>"
        #
        try:
            #
            test_result11 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result12 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit2)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result11 + "\n"
            msg += "Test recognition result 2: \n" + test_result12 + "\n"
            #
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result11, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result12, expectResult=test_expect12)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00554_NRIR_osr20_feature_NewW3CGram_NewGrammar_lexicon(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/NewW3CGram/NewGrammar_lexicon

        This script loads a grammar with "lexicon" to point at a dictionary.
        Expect:
        1) [Test Case]
            a) Send audio "blue" similar to "2". Expect recognition result "2"

        parameter ignored:
            - swirec_load_adjusted_speedvsaccuracy busy
        """
        client = gRPCClient()
        
        # the pronounciation of '2' is "blue".
        test_audio = "NRIR_blue2.wav"
        test_audio_format = 'pcm'
        test_grammar_type = 'uri_grammar'
        test_grammar_data = 'NRIR_digit_lexicon.xml'
        test_media_type = 'srgsxml'
        test_expect1 = "<SWI_literal>2</SWI_literal>"

        test_grammar_uri = client.test_res_url + test_grammar_data
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = [test_recogRes]
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
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

    def test00555_NRIR_osr20_feature_Grammar_SWI_vars_precedence(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/Grammar/SWI_vars/precedence

        Tests precedence in setting values in grammar.
        Expect:
        1) [Test Case]
            a)  pass in SWI_vars.color=red to a grammar that sets color="blue". Expect result "blue"
            b)  pass in SWI_vars.color=red;color=yellow to a grammar. Expect result "red"
            c)  pass in SWI_vars.color=red;SWI_vars.color=yellow to a grammar. Expect result "yellow"

        parameter ignored:
            - swirec_load_adjusted_speedvsaccuracy busy
            - SWIrecAcousticStateReset REC
        """
        client = gRPCClient()
        
        # test 1: pass in SWI_vars.color=red to a grammar that sets color="blue"
        test_grammar_data1 = 'NRIR_color_blue.grxml?SWI_vars.color=red'
        test_grammar_type1 = 'uri_grammar'
        test_media_type1 = 'srgsxml'
        test_audio1 = "NRIR_blue2.wav"
        test_audio_format1 = 'pcm'
        test_expect1 = "<color.+>blue</color>"
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        
        # test 2: pass in SWI_vars.color=red;color=yellow to a grammar 
        test_grammar_data2 = 'NRIR_color_var.grxml?SWI_vars.color=red;color=yellow'
        test_grammar_type2 = 'uri_grammar'
        test_media_type2 = 'srgsxml'
        test_audio2 = "NRIR_blue2.wav"
        test_audio_format2 = 'pcm'
        test_expect2 = "<SWI_meaning>red</SWI_meaning>"
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        test_recogParams2 = client.recognition_parameters(audioFormat=test_audio_format2)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams2, recogRes=test_recogRes2)

        # test 3: pass in SWI_vars.color=red;SWI_vars.color=yellow to a grammar 
        test_grammar_data3 = 'NRIR_color_var.grxml?SWI_vars.color=red;x=toto;SWI_vars.color=yellow'
        test_grammar_type3 = 'uri_grammar'
        test_media_type3 = 'srgsxml'
        test_audio3 = "NRIR_blue2.wav"
        test_audio_format3 = 'pcm'
        test_expect3 = "<SWI_meaning>yellow</SWI_meaning>"
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_uri3, mediaType=test_media_type3)
        test_recogParams3 = client.recognition_parameters(audioFormat=test_audio_format3)
        test_recogRes3 = [test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams3, recogRes=test_recogRes3)
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
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00556_NRIR_osr20_feature_Grammar_SWI_vars_precedence_import(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/Grammar/SWI_vars/precedence

        Tests precedence in setting values in grammar.
        Expect
        1) [Test Case]
            a) check SWI_vars can be propagated into an imported grammar: <ruleref uri="color_var.grxml?SWI_vars.color=SWI_vars.color"/>. Expect "red"
            b) check that SWI_vars is not automatically propagated into an imported grammar: <ruleref uri="color_var_undefined.grxml"/> (SWI_vars.color should be undefined in color_var_undefined.grxml). Expect "blue"
            c) pass in SWI_vars.color=red to a grammar that reassigns SWI_vars.color to yellow, then passes it into the imported grammar. Expect "yellow"

        parameter ignored:
            - swirec_load_adjusted_speedvsaccuracy busy
            - SWIrecAcousticStateReset REC
        """
        client = gRPCClient()
        
        # test 1: check SWI_vars can be propagated into an imported grammar: <ruleref uri="color_var.grxml?SWI_vars.color=SWI_vars.color"/>
        test_grammar_data1 = 'NRIR_import_color_var.grxml?SWI_vars.color=red'
        test_grammar_type1 = 'uri_grammar'
        test_media_type1 = 'srgsxml'
        test_audio1 = "NRIR_blue2.wav"
        test_audio_format1 = 'pcm'
        test_expect1 = "<color.+>red</color>"
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        
        # test 2: check that SWI_vars is not automatically propagated into an imported grammar: <ruleref uri="color_var_undefined.grxml"/> (SWI_vars.color should be undefined in color_var_undefined.grxml)
        test_grammar_data2 = 'NRIR_import_color_var3.grxml?SWI_vars.color=red'
        test_grammar_type2 = 'uri_grammar'
        test_media_type2 = 'srgsxml'
        test_audio2 = "NRIR_blue2.wav"
        test_audio_format2 = 'pcm'
        test_expect2 = "<color.+>blue</color>"
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        test_recogParams2 = client.recognition_parameters(audioFormat=test_audio_format2)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams2, recogRes=test_recogRes2)

        # test 3: pass in SWI_vars.color=red to a grammar that reassigns SWI_vars.color to yellow, then passes it into the imported grammar
        test_grammar_data3 = 'NRIR_import_color_var2.grxml?SWI_vars.color=red'
        test_grammar_type3 = 'uri_grammar'
        test_media_type3 = 'srgsxml'
        test_audio3 = "NRIR_blue2.wav"
        test_audio_format3 = 'pcm'
        test_expect3 = "<color.+>yellow</color>"
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type3, grammarData=test_grammar_uri3, mediaType=test_media_type3)
        test_recogParams3 = client.recognition_parameters(audioFormat=test_audio_format3)
        test_recogRes3 = [test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams3, recogRes=test_recogRes3)
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
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
    
    def test00557_NRIR_proton_feature_parameter_test_script_robust_compile_time_script(self):
        """
        NR IR Converted testcases:
            # ./proton_feature/parameter_test/script/robust_compile_time_script

        Tests swirec_enable_robust_compile. Load 1 grammar that sets parameter and another that does not.
        Both grammars have word "to#go" that cannot be pronounced (the word is not found in a dictionary and an automatic pronunciation cannot be generated).

        Expect:
        1) [Test Case]
            a) First grammar sets parameter swirec_enable_robust_compile allows to ignore the nonsense entries. Expect successful recognition "<SWI_literal>gladewater texas</SWI_literal>".
            b) Second grammar doesn't set parameter swirec_enable_robust_compile. Expect Recognizer aborts compilation because "to#go" cannot be pronounced.

        parameter ignored:
        - swirec_load_adjusted_speedvsaccuracy busy
        - SWIrecAcousticStateReset REC
        """
        client = gRPCClient()
        
        test_audio = "NRIR_gladewater_texas.ulaw"
        test_audio_format = 'ulaw'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        # 1) a)
        test_grammar_data1 = 'NRIR_gt_imports_robust_togo.grxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_expect1 = "<SWI_literal>gladewater texas</SWI_literal>"
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes1)
        # 1) b)
        test_grammar_data2 = 'NRIR_robust_gt_imports_togo_.grxml'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type)
        test_recogRes2 = [test_recogRes2]
        test_expect21 = "code: 400"
        test_expect22 = 'message: "Bad Request"'
        test_expect23 = 'details: "Failed to load RecognitionResource at index'
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes2)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit2)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect21)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect22)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect23)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)

    def test00558_NRIR_proton_feature_parameter_test_swirec_word_conf_enabled_parallel_gram_PERL(self):
        """
        NR IR Converted testcases:
            ./proton_feature/parameter_test/swirec_word_conf_enabled_parallel_gram_PERL

        Test uses "<city> <state>" grammar which returns the word confidence via the keys city_conf and state_conf.
        Test uses "<first name> <last name>" with word confidence returned in the keys first_conf and last_conf.
        The first grammar has word confidence disabled and the second is enabled so we expect the returned conf values to be zero in the first and >0 in the second.

        Expect:
        1) [Test Case]
            a) swirec_word_confidence_enabled DISABLED. The first utt should match grammar 1 and the returned values for city_conf and state_conf should be zero.
            b) swirec_word_confidence_enabled ENABLED. The second utt should match grammar 2 and the returned values for fisrt_conf and last_conf should be > 0

        parameter ignored:
        - swirec_load_adjusted_speedvsaccuracy busy
        - SWIrecAcousticStateReset REC
        """
        client = gRPCClient()
        
        test_audio_format = 'ulaw'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'

        test_grammar_data1 = 'NRIR_word_conf_disabled.xml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_grammar_data2 = 'NRIR_word_conf2_enabled.xml'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type)
        test_recogRes = [test_recogRes1, test_recogRes2]

        test_audio1 = "NRIR_gladewater_texas.ulaw"
        test_expect11 = "city_conf"
        test_expect12 = "state_conf"
        test_expect13 = "SWI_meaning"

        test_audio2 = "NRIR_SS_MapQuest000904_utt000.ulaw"
        test_expect21 = "first_conf"
        test_expect22 = 'last_conf'
        test_expect23 = 'SWI_meaning'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recInit = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes)
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
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
            # Validate confidence values
            city_conf = float(self.getFirstXmlOccurrence(xmlTarget="city_conf", result=test_result1))
            state_conf = float(self.getFirstXmlOccurrence(xmlTarget="state_conf", result=test_result1))
            first_conf = float(self.getFirstXmlOccurrence(xmlTarget="first_conf", result=test_result2))
            last_conf = float(self.getFirstXmlOccurrence(xmlTarget="last_conf", result=test_result2))
            self.assertEquals(city_conf, 0)
            self.assertEquals(state_conf, 0)
            self.assertTrue(first_conf > 0)
            self.assertTrue(last_conf > 0)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test00559_NRIR_proton_feature_parameter_test_swirec_word_confidence_enabled_PERL(self):
        """
        NR IR Converted testcases:
            ./proton_feature/parameter_test/swirec_word_confidence_enabled_PERL

        Test uses "<city> <state>" grammar which returns the word confidence via the keys city_conf and state_conf. All recognitions use the same audio.
        The first grammar has word confidence not set, second has parameter disabled, and last has parameter set in grammar.

        Expect:
        1) [Test Case]
            a) swirec_word_confidence_enabled NOT SET (default is disabled). The first utt should match grammar 1 and the returned values for city_conf and state_conf should be zero.
            b) swirec_word_confidence_enabled DISABLED. The first utt should match grammar 1 and the returned values for city_conf and state_conf should be zero.
            b) swirec_word_confidence_enabled ENABLED. The second utt should match grammar 2 and the returned values for city_conf and state_conf should be > 0

        parameter ignored:
        - swirec_load_adjusted_speedvsaccuracy busy
        - SWIrecAcousticStateReset REC
        """
        client = gRPCClient()
        
        test_audio_format = 'ulaw'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_audio = "NRIR_gladewater_texas.ulaw"
        # 1) a)
        test_grammar_data1 = 'NRIR_word_conf_notset.xml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes1)
        test_expect11 = "city_conf"
        test_expect12 = "state_conf"
        test_expect13 = "SWI_meaning"
        # 1) b)
        test_grammar_data2 = 'NRIR_word_conf_disabled.xml'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes2)
        test_expect21 = "city_conf"
        test_expect22 = 'state_conf'
        test_expect23 = 'SWI_meaning'
        # 1) c)
        test_grammar_data3 = 'NRIR_word_conf_enabled.xml'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri3, mediaType=test_media_type)
        test_recogRes3 = [test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes3)
        test_expect31 = "city_conf"
        test_expect32 = 'state_conf'
        test_expect33 = 'SWI_meaning'
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit3)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 2: \n" + test_result3 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect11)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect12)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect13)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect21)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect22)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect23)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect31)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect32)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect33)
            # Validate confidence values
            city_conf_1 = float(self.getFirstXmlOccurrence(xmlTarget="city_conf", result=test_result1))
            state_conf_1 = float(self.getFirstXmlOccurrence(xmlTarget="state_conf", result=test_result1))
            city_conf_2 = float(self.getFirstXmlOccurrence(xmlTarget="city_conf", result=test_result2))
            state_conf_2 = float(self.getFirstXmlOccurrence(xmlTarget="state_conf", result=test_result2))
            city_conf_3 = float(self.getFirstXmlOccurrence(xmlTarget="city_conf", result=test_result3))
            state_conf_3 = float(self.getFirstXmlOccurrence(xmlTarget="state_conf", result=test_result3))
            self.assertEquals(city_conf_1, 0)
            self.assertEquals(state_conf_1, 0)
            self.assertEquals(city_conf_2, 0)
            self.assertEquals(state_conf_2, 0)
            self.assertTrue(city_conf_3 > 0)
            self.assertTrue(state_conf_3 > 0)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test00560_NRIR_proton_feature_parameter_test_swirec_enable_robust_compile_PERL(self):
        """
        NR IR Converted testcases:
            ./proton_feature/parameter_test/swirec_enable_robust_compile_PERL

        Tests swirec_enable_robust_compile. Load 1 grammar that sets parameter and another that does not.
        Both grammars have word "nana#nak" that cannot be pronounced (the word is not found in a dictionary and an automatic pronunciation cannot be generated).

        Expect:
        1) [Test Case]
            a) swirec_word_confidence_enabled ENABLED. Grammar load is successful. 
                i)  nananak cannot be recognized because "nana#nak" cannot be pronounced.
                ii) gladewater texas is recognized.
            b) swirec_word_confidence_enabled DISABLED. Grammar load fails because "nana#nak" cannot be pronouced.

        parameter ignored:
        - swirec_load_adjusted_speedvsaccuracy busy
        - SWIrecAcousticStateReset REC
        """
        client = gRPCClient()
        
        test_audio_format = 'ulaw'
        test_grammar_type = 'uri_grammar'
        test_media_type = 'srgsxml'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        # 1) a)
        test_grammar_data1 = 'NRIR_robust_nananak_.grxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type)
        test_recogRes_1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_1)
        # 1) a) i)
        test_audio1 = "NRIR_nananak.ulaw"
        test_not_in_result_1 = "<SWI_literal>nananak</SWI_literal>"
        test_expect1 = "NO_MATCH"
        # 1) a) ii)
        test_audio2 = "NRIR_gladewater_texas.ulaw"
        test_expect2 = "<SWI_literal>gladewater texas</SWI_literal>"

        # 1) b)
        test_grammar_data2 = 'NRIR_robust_0_nananak_.grxml'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type)
        test_recogRes_2 = [test_recogRes1, test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes_2)
        test_expect31 = "code: 400"
        test_expect32 = 'message: "Bad Request"'
        test_expect33 = 'details: "Failed to load RecognitionResource at index'
        #
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit1)
            time.sleep(1)
            test_result3 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit2)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            msg += "Test recognition result 3: \n" + test_result3 + "\n"
            # self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertNotRecognitionResult(inputToCheck=test_result1, undesiredResult=test_not_in_result_1)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect31)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect32)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect33)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)

    def test00561_NRIR_proton_feature_DA_word_list_script_da_wordlist_many_userdict(self):
        """
        NR IR Converted testcases:
            ./proton_feature/DA_word_list/script/da_wordlist_many_userdict 
    
        Test recognition with simple grammar and extended many_userdict grammar.
        The same audio files are used
        Expect:
        1) [Test Case]
            a) Simple grammar loaded.
                i)   Audio utterance "Atlanta" not part of grammar words. Expect not in recognition result.
                ii)  Audio utterance "Springfield" not part of grammar words. Expect not in recognition result.
            b) Many Userdict grammar loaded.
                i)   Audio utterance "Legrange", expect "<SWI_meaning>ThisOneNeedsaUserDictionary</SWI_meaning>"
                ii)  Audio utterance "Atlanta", expect "<SWI_meaning>An0ther0neNeedsaUserDicti0nary</SWI_meaning>"
                iii) Audio utterance "Springfield", expect "<SWI_meaning>w0ntRec0gnizeThis0neEitherwith0utsauserdictionary</SWI_meaning>"
        """
        client = gRPCClient()

        # 1) a)
        test_grammar_data1 = 'NRIR_DA_word_list_simple.gram'
        test_grammar_type1 = 'uri_grammar'
        test_media_type1 = 'xswigrammar'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_audio_format1 = 'ulaw'
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogRes_1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes_1) 
        # 1) a) i)
        test_audio11 = "NRIR_atlanta.ulaw"
        test_not_in_result11 = "<SWI_meaning>An0ther0neNeedsaUserDicti0nary</SWI_meaning>"
        # 1) a) ii)
        test_audio12 = "NRIR_springfield.ulaw"
        test_not_in_result12 = "<SWI_meaning>w0ntRec0gnizeThis0neEitherwith0utsauserdictionary</SWI_meaning>"

        # 1) b)
        test_grammar_data2 = 'NRIR_DA_word_list_many_userdict.gram'
        test_grammar_type2 = 'uri_grammar'
        test_media_type2 = 'xswigrammar'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_audio_format2 = 'ulaw'
        test_recogParams2 = client.recognition_parameters(audioFormat=test_audio_format2)
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        test_recogRes_2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams2, recogRes=test_recogRes_2) 
        # 1) b) i)
        test_audio21 = "NRIR_legrange.ulaw"
        test_expect21 = "<SWI_meaning>ThisOneNeedsaUserDictionary</SWI_meaning>"
        # 1) b) ii)
        test_audio22 = "NRIR_atlanta.ulaw"
        test_expect22 = "<SWI_meaning>An0ther0neNeedsaUserDicti0nary</SWI_meaning>"
        # 1) b) iii)
        test_audio23 = "NRIR_springfield.ulaw"
        test_expect23 = "<SWI_meaning>w0ntRec0gnizeThis0neEitherwith0utsauserdictionary</SWI_meaning>"
        #
        try:
            test_result11 = client.qa_nr_recognize_test_func1(audioInput=test_audio11, recInit=test_recInit1)
            time.sleep(1)
            test_result12 = client.qa_nr_recognize_test_func1(audioInput=test_audio12, recInit=test_recInit1)
            time.sleep(1)
            test_result21 = client.qa_nr_recognize_test_func1(audioInput=test_audio21, recInit=test_recInit2)
            time.sleep(1)
            test_result22 = client.qa_nr_recognize_test_func1(audioInput=test_audio22, recInit=test_recInit2)
            time.sleep(1)
            test_result23 = client.qa_nr_recognize_test_func1(audioInput=test_audio23, recInit=test_recInit2)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result11 + "\n"
            msg += "Test recognition result 2: \n" + test_result12 + "\n"
            msg += "Test recognition result 3: \n" + test_result21 + "\n"
            msg += "Test recognition result 4: \n" + test_result22 + "\n"
            msg += "Test recognition result 5: \n" + test_result23 + "\n"
            #
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertNotRecognitionResult(inputToCheck=test_result11, undesiredResult=test_not_in_result11)
            self.assertNotRecognitionResult(inputToCheck=test_result12, undesiredResult=test_not_in_result12)
            self.assertRecognitionResult(inputToCheck=test_result21, expectResult=test_expect21)
            self.assertRecognitionResult(inputToCheck=test_result22, expectResult=test_expect22)
            self.assertRecognitionResult(inputToCheck=test_result23, expectResult=test_expect23)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00562_NRIR_spectrum_feature_interpolated_LM_rec_neg_interpolated_LM_PERL (self):
        """
        NR IR Converted testcases:
            ./spectrum_feature/interpolated_LM/rec_neg_interpolated_LM_PERL 

        Interpolated component Lm negative test cases.
        3 negative test cases converted out of 5.
        3 recognitions, all use the same audio file but different grammar files.
        Expect:
        1) [Test Case]
            a) (NRIR case 1) make sure that internal ref must be binding="static" otherwise error is shown. Here binding="dynamic", expect failure "code 400 Bad Request Failed to load Recognition Resource"
            b) (NRIR case 3) component offset attribute is allowed only for smoothing=interpolated'. Here (line 8) not set. Expect failure "code 400 Bad Request Failed to load Recognition Resource"
            b) (NRIR case 4) component priority attribute is not allowed only for smoothing=interpolated'. Here (line 8) not set. Expect failure "code 400 Bad Request Failed to load Recognition Resource"
        """
        client = gRPCClient()
        
        # Common audio file.
        test_audio_format = 'ulaw'
        test_grammar_type = 'uri_grammar'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_audio = "NRIR_I_would_like_to_see_the_movie.ulaw"

        # (NRIR case 1) make sure that internal ref must be binding="static" otherwise error is shown. Here binding="dynamic", expect failure "code 400 Bad Request Failed to load Recognition Resource"
        test_grammar_data1 = 'NRIR_rec_neg_interpolated_LM_1.grxml'
        test_media_type1 = 'srgsxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes1)
        test_expect11 = "code: 400"
        test_expect12 = "message: \"Bad Request\""
        test_expect13 = "details: \"Failed to load RecognitionResource at index"

        # (NRIR case 3) component offset attribute is allowed only for smoothing=interpolated'. Here (line 8) not set. Expect failure "code 400 Bad Request Failed to load Recognition Resource"
        test_grammar_data2 = 'NRIR_rec_neg_interpolated_LM_3.grxml'
        test_media_type2 = 'srgsxml'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes2)
        test_expect21 = "code: 400"
        test_expect22 = "message: \"Bad Request\""
        test_expect23 = "details: \"Failed to load RecognitionResource at index"

        # (NRIR case 4) component priority attribute is not allowed only for smoothing=interpolated'. Here (line 8) not set. Expect failure "code 400 Bad Request Failed to load Recognition Resource"
        test_grammar_data3 = 'NRIR_rec_neg_interpolated_LM_4.grxml'
        test_media_type3 = 'srgsxml'
        test_grammar_uri3 = client.test_res_url + test_grammar_data3
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri3, mediaType=test_media_type3)
        test_recogRes3 = [test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes3)
        test_expect31 = "code: 400"
        test_expect32 = "message: \"Bad Request\""
        test_expect33 = "details: \"Failed to load RecognitionResource at index"
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
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect23)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect31)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect32)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect33)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            time.sleep(20)

    def test00563_NRIR_osr20_feature_Grammar_VXI_Map_Property_AutoUpdate_Case1 (self):
        """
        NR IR Converted testcases:
            ./osr20_feature/Grammar/VXI_Map_Property/AutoUpdate_Case1

        Testing VXIMap Property AUTO_UPDATE
        This it test prevention of an update to an existing grammar in Cache
        
        Expect:
        1) [Test Case]
            a) Load grammar that contains "airwrench" with "air_wrench" audio. Expect "<SWI_meaning>{SWI_literal:airwrench}</SWI_meaning>".
            b) Load grammar that doesn't contain "airwrench", but contains "air", with "air_wrench" audi. Expect "<SWI_meaning>{SWI_literal:air}</SWI_meaning>"
        """
        client = gRPCClient()
        
        # Common audio file.
        test_audio_format = 'ulaw'
        test_grammar_type = 'uri_grammar'
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_audio = "NRIR_air_wrench.ulaw"
        
        test_grammar_data1 = 'NRIR_item_const_cp_1.xml'
        test_media_type1 = 'srgsxml'
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes1)
        test_expect1 = "<SWI_meaning>{SWI_literal:airwrench}</SWI_meaning>"
        
        test_grammar_data2 = 'NRIR_item_const_cp_2.xml'
        test_media_type2 = 'srgsxml'
        test_grammar_uri2 = client.test_res_url + test_grammar_data2
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri2, mediaType=test_media_type2)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams, recogRes=test_recogRes2)
        test_expect2 = "<SWI_meaning>{SWI_literal:air}</SWI_meaning>"
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
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test00564_NRIR_osr20_feature_DigitConstraints_DigitConstraints1(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/DigitConstraints/DigitConstraints1

        This test excercises changes in the digits built-in grammar, particularly the usage of constraints lists.
        Expect:
            1) [Test Case]
                a) Activate digits builtin grammar with constraints, send audio "2", expect successful recognition.
                b) Activate digits builtin grammar with constraints, send audio "8", expect successful recognition.
                c) Activate digits builtin grammar with constraints, send audio "3" not part of constraints list, expect no match.
        
        Ignored commands:
        - SWIrecRecognizerCompute REC. Does not affect purpose of test case.
        """
        client = gRPCClient()
        #
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits?entries=' + client.test_res_url + 'NRIR_simple_constraints.txt'
        
        # 1) a) Valid recognition.
        test_audio1 = "NRIR_2.wav"
        test_expect1 = "<instance>2</instance>"
        test_audio_format1 = 'pcm'
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        
        # 1) b) Valid Recognition.
        test_audio2 = "NRIR_4.wav"
        test_expect2 = "<instance>4</instance>"
        test_audio_format2 = 'pcm'
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recogParams2 = client.recognition_parameters(audioFormat=test_audio_format2)
        test_recogRes2 = [test_recogRes2]
        test_recInit2 = client.recognition_init_repeated(recogParam=test_recogParams2, recogRes=test_recogRes2)
        
        # 1) c) Invalid Recognition.
        test_audio3 = "NRIR_3.wav"
        test_audio_format3 = 'pcm'
        #test_expect3 = "SWIrec_STATUS_NO_MATCH"
        #test_expect3 =  "<result>.*nomatch.*/result>"
        test_expect3 = "NO_MATCH"
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recogParams3 = client.recognition_parameters(audioFormat=test_audio_format3)
        test_recogRes3 = [test_recogRes3]
        test_recInit3 = client.recognition_init_repeated(recogParam=test_recogParams3, recogRes=test_recogRes3)
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
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00565_NRIR_osr20_feature_W3CGram_Case2_Test_Parser_Test_Parser_AIO_PERL_1(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/W3CGram/Case2_Test_Parser/Test_Parser_AIO_PERL

        Test case runs (straightforward) recognition.
        Loads a grammar, sends an audio utterance and expects expression in the result.
        Expect
        1) [Test Case]
            a) Load NRIR_alternative-null.grxml with "hello world" utterance. Expect "<SWI_literal>hello world</SWI_literal>".
        """
        client = gRPCClient()
        #
        test_grammar_data1 = 'NRIR_alternative-null.grxml'
        test_grammar_type1 = 'uri_grammar'
        test_media_type1 = 'srgsxml'
        test_audio1 = "NRIR_hello_world.ulaw"
        test_audio_format1 = 'ulaw'
        test_expect1 = "<SWI_literal>hello world</SWI_literal>"
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
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00566_NRIR_osr20_feature_W3CGram_Case2_Test_Parser_Test_Parser_AIO_PERL_2(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/W3CGram/Case2_Test_Parser/Test_Parser_AIO_PERL

        Test case runs (straightforward) recognition.
        Loads a grammar, sends an audio utterance and expects expression in the result.
        Expect
        1) [Test Case]
            a) Load NRIR_alternatives-one-with-weight.grxm with "chocolate" utterance. Expect "<SWI_literal>chocolate</SWI_literal>".
        """
        client = gRPCClient()
        #
        test_grammar_data1 = 'NRIR_alternatives-one-with-weight.grxml'
        test_grammar_type1 = 'uri_grammar'
        test_media_type1 = 'srgsxml'
        test_audio1 = "NRIR_chocolate.ulaw"
        test_audio_format1 = 'ulaw'
        test_expect1 = "<SWI_literal>chocolate</SWI_literal>"
        test_grammar_uri1 = client.test_res_url + test_grammar_data1
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1, mediaType=test_media_type1)
        test_recogParams1 = client.recognition_parameters(audioFormat=test_audio_format1)
        test_recogRes1 = [test_recogRes1]
        test_recInit1 = client.recognition_init_repeated(recogParam=test_recogParams1, recogRes=test_recogRes1)
        try:
            #
            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit1)
            time.sleep(1)
            #
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00567_NRIR_osr20_feature_W3CGram_Case2_Test_Parser_Test_Parser_AIO_PERL_3(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/W3CGram/Case2_Test_Parser/Test_Parser_AIO_PERL

        Test case runs (straightforward) recognition.
        Loads a grammar, sends an audio utterance and expects expression in the result.
        Expect
        1) [Test Case]
            a) Load NRIR_meta-http.grxml with "placeholder" utterance. Expect "<SWI_literal>placeholder</SWI_literal>".
        """
        client = gRPCClient()
        #
        test_grammar_data1 = 'NRIR_meta-http.grxml'
        test_grammar_type1 = 'uri_grammar'
        test_media_type1 = 'srgsxml'
        test_audio1 = "NRIR_placeholder.ulaw"
        test_audio_format1 = 'ulaw'
        test_expect1 = "<SWI_literal>placeholder</SWI_literal>"
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
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00568_NRIR_osr20_feature_W3CGram_Case2_Test_Parser_Test_Parser_AIO_PERL_4(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/W3CGram/Case2_Test_Parser/Test_Parser_AIO_PERL

        Test case runs (straightforward) recognition.
        Loads a grammar, sends an audio utterance and expects expression in the result.
        Expect
        1) [Test Case]
            a) Load NRIR_repeat-m-n-times.grxml with "well well" utterance. Expect "<SWI_literal>well well</SWI_literal>".
        """
        client = gRPCClient()
        #
        test_grammar_data1 = 'NRIR_repeat-m-n-times.grxml'
        test_grammar_type1 = 'uri_grammar'
        test_media_type1 = 'srgsxml'
        test_audio1 = "NRIR_well_well.ulaw"
        test_audio_format1 = 'ulaw'
        test_expect1 = "<SWI_literal>well well</SWI_literal>"
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
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test00569_NRIR_osr20_feature_W3CGram_Case2_Test_Parser_Test_Parser_AIO_PERL_5(self):
        """
        NR IR Converted testcases:
            ./osr20_feature/W3CGram/Case2_Test_Parser/Test_Parser_AIO_PERL

        Test case runs (straightforward) recognition.
        Loads a grammar, sends an audio utterance and expects expression in the result.
        Expect
        1) [Test Case]
            a) Load NRIR_sequence-ruleref.grxml with "open the door" utterance. Expect "<SWI_literal>open the door</SWI_literal>".
        """
        client = gRPCClient()
        #
        test_grammar_data1 = 'NRIR_sequence-ruleref.grxml'
        test_grammar_type1 = 'uri_grammar'
        test_media_type1 = 'srgsxml'
        test_audio1 = "NRIR_open_the_door.ulaw"
        test_audio_format1 = 'ulaw'
        test_expect1 = "<SWI_literal>open the door</SWI_literal>"
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
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()


    def test_dynamicLinkedGrammar_yes(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw' & Automatic MediaType
        Expect:
        1) [Test case] NRC recognize return should be successful
        """ 

        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'yes.ulaw'
        test_grammar = "grammars/grammars/wrapper_level_1_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = None
        test_grammar_uri = client.test_res_url + test_grammar
        
        print("Test grammar URI: " + test_grammar_uri + "\n")
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="API", value="SWIrecGrammarLoad")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="API", value="SWIrecGrammarActivate")
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GURI0", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRNM", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
    
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()
            

    def test_dynamicLinkedGrammar_digit(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw' & Automatic MediaType
        Expect:
        1) [Test case] NRC recognize return should be successful
            
         """ 

        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = '1.ulaw'
        test_grammar = "grammars/grammars/wrapper_level_1.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = None
        test_grammar_uri = client.test_res_url + test_grammar
        
        print("Test grammar URI: " + test_grammar_uri + "\n")
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_result = ""
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.*ONE</input><instance><SWI_literal>ONE</SWI_literal><SWI_grammarName>.*</SWI_grammarName><SWI_meaning>{SWI_literal:ONE}</SWI_meaning></instance></interpretation>.*"

        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="API", value="SWIrecGrammarLoad")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="API", value="SWIrecGrammarActivate")
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GURI0", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRNM", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(2)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()


    def test_dynamicLinkedGrammar_Invalid(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw' & Automatic MediaType
        Expect:
        1) [Test case] NRC recognize return should be successful
            
         """ 

        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = '1.ulaw'
        test_grammar = "grammars/grammars/wrapper_level_Invalid.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = None
        test_grammar_uri = client.test_res_url + test_grammar
        
        print("Test grammar URI: " + test_grammar_uri + "\n")
 
        test_result = ""

        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect1, status_code=400, status_message="Bad Request")
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="API", value="SWIrecGrammarLoad")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(5)
            msg = "Test result:\n" + test_result + "\n"
            print(msg)    
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0201_Credit_Card_Masking_with_BuiltinGrammarDigit_1(self):
        """
        Test NRC recognition for Credit Card Masking feature with Builtin Digit grammar with audio '5610591081018250.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify in the NRC call log the number 5610591081018250 has to be masked with the message "FluentD redacted possible CCN" 
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "5610591081018250.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>5610591081018250<\/instance.+\/interpretation.+\/result>"
        token_value = "FluentD redacted possible CCN"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")
        test_record_1.add_token_to_checklist(evnt="CCM", token="CNN", value=token_value)
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(3)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()
    
            
    def test0202_Credit_Card_Masking_with_BuiltinGrammarDigit_2(self):
        """
        Test NRC recognition for Credit Card Masking feature with Builtin Digit grammar with audio '4312367891028100.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify in the NRC call log the number 4312367891028100 has to be masked with the message "FluentD redacted possible CCN" 
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "4312367891028100.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\\/digits.+<instance>4312367891028100<\\/instance.+\\/interpretation.+\\/result>"
        token_value = "FluentD redacted possible CCN"
        
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        
        
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")
        test_record_1.add_token_to_checklist(evnt="CCM", token="CNN", value=token_value)
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(3)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            #test_record_1.add_token_to_checklist(evnt="CCM", token="CNN", value=token_value)
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()
            kafka.cleanup()
    
    
            
    def test0203_Credit_Card_Masking_with_BuiltinGrammarDigit_3(self):
        """
        Test NRC recognition for Credit Card Masking feature with Builtin Digit grammar with audio '1234567891011121.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify in the NRC call log the number 1234567891011121 has to be masked with the message "FluentD redacted possible CCN" 
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = "1234567891011121.ulaw"
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\\/digits.+<instance>1234567891011121<\\/instance.+\\/interpretation.+\\/result>"
        token_value = "FluentD redacted possible CCN"
        
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        
        
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")
        test_record_1.add_token_to_checklist(evnt="CCM", token="CNN", value=token_value)
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(3)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            #test_record_1.add_token_to_checklist(evnt="CCM", token="CNN", value=token_value)
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()
            kafka.cleanup()

    def test0204_UriGrammar_Name_SteveJackson(self):
        """
        Test NRC recognition URI grammar with audio 'Name.ulaw.raw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/srgs+xml
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'Name.ulaw.raw'
        test_grammar = "names.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_meaning>steve_jackson</SWI_meaning><SWI_literal>steve_jackson</SWI_literal>.+</instance></interpretation></result>"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/srgs+xml")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"" + test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(3)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            time.sleep(3)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0205_UriGrammar_Stations333_Cuba(self):
        """
        Test NRC recognition URI grammar with audio 'NRIR_Cuba.wav'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/srgs+xml
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'NRIR_Cuba.wav'
        test_audio_format = 'pcm'
        test_grammar = "stations333.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_meaning>CUBAMO</SWI_meaning><SWI_literal>cuba</SWI_literal>.+</instance></interpretation></result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/srgs+xml")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"" + test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(3)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0206_UriGrammar_EquipID_E_One(self):
        """
        Test NRC recognition URI grammar with audios 'E_one.ulaw.raw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/srgs+xml
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'E_one.ulaw.raw'
        test_grammar = "equipID.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_meaning>E 1</SWI_meaning><SWI_literal>E one</SWI_literal>.+</instance></interpretation></result>"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/srgs+xml")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"" + test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(3)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0207_UriGrammar_TrainID_CCRMHOH_One_Ten(self):
        """
        Test NRC recognition URI grammar with audios 'CCRMHOH1Ten.ulaw.raw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Grammar related events all presented in the call log, including: SWIgrld;
            b) For event SWIrcst, value of Token GRMT should be application/srgs+xml
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_audio = 'CCRMHOH1Ten.ulaw.raw'
        test_grammar = "TrainID.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_meaning>CCRMHOH110</SWI_meaning><SWI_literal>C_C_R_M_H_O_H one ten</SWI_literal>.+</instance></interpretation></result>"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrcst", token="GRMT", value="application/srgs+xml")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"" + test_grammar_uri)

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(3)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test0208_UriGrammar_Genesys_Invalid_Grammar(self):
        """
        Test NRC recognition URI grammar with audio 'one.ulaw'
        Expect:
        1) [Test case] NRC recognize return should return NO_MATCH
        """
        client = gRPCClient()

        test_audio = 'one.ulaw'
        test_grammar = "TrainID.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "NO_MATCH"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            # self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            # self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            time.sleep(20)

    def test0209_Genesys_UriGrammar_InvalidAudio(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw'
        Expect:
        1)
            a) Audio has invalid frequency. Expect "code 404: No Speech (audio silence)"
        """
        client = gRPCClient()

        test_audio = 'A_One.wav'
        test_grammar = "equipID.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect1 = "code: 404"
        test_expect2 = 'message: \"No Speech\"'

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            time.sleep(20)

    def test0210_Genesys_UriGrammar_askPassport_numbers(self):
        """
        Test NRC recognition URI grammar with audios 'de_2021.ulaw.raw' and 'de_2021596.ulaw.raw'
        Expect:
        1)1
            a) NRC return successful recognition
        """
        client = gRPCClient()

        test_audio1 = "de_2021.ulaw.raw"
        test_audio2 = "de_2021596.ulaw.raw"
        test_language = 'de-DE'
        test_grammar = "ask_passport.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect1 = "<SWI_literal>zwei null zwei eins</SWI_literal>.+<SWI_meaning>{slot:2021}</SWI_meaning>"
        test_expect2 = "<SWI_literal>zwei null zwei eins fünf neun sechs</SWI_literal>.+<SWI_meaning>{slot:2021596}</SWI_meaning>"
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result1 = client.qa_nr_recognize_test_func1(audioInput=test_audio1, recInit=test_recInit)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit)
            time.sleep(1)
            msg = ""
            msg += "Test recognition result 1: \n" + test_result1 + "\n"
            msg += "Test recognition result 2: \n" + test_result2 + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            time.sleep(20)

    def test0211_Genesys_UriGrammar_askPassport_alphanumerics(self):
        """
        Test NRC recognition URI grammar with audio 'de_o20215956.ulaw.raw'
        Expect:
        1)1
            a) NRC recognize return successful
        """
        client = gRPCClient()

        test_audio = "de_o20215956.ulaw.raw"
        test_language = 'de-DE'
        test_grammar = "ask_passport.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<SWI_literal>o zwei null zwei eins fünf neun fünf sechs</SWI_literal>.+<SWI_meaning>{slot:O20215956}</SWI_meaning>"
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = ""
            msg += "Test recognition result 1: \n" + test_result + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            time.sleep(20)

    def test0212_Genesys_UriGrammar_askPassport_noMatch(self):
        """
        Test NRC recognition URI grammar with audio 'de_a20215956.ulaw.raw'
        Expect:
        1)1
            a) NRC recognize return NO_MATCH
        """
        client = gRPCClient()

        test_audio = "de_a20215956.ulaw.raw"
        test_language = 'de-DE'
        test_grammar = "ask_passport.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "NO_MATCH"
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        try:

            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = ""
            msg += "Test recognition result 1: \n" + test_result + "\n"
            print(msg)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            time.sleep(20)