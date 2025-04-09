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
class NRCTestRecognitionLang(TestFixture):
    """ NRC recognition resource language test"""

    def test001_NRCRecogLangGeneric1(self):
        """
        Test NRC multi-language recognition generic with default language (en-US), default test audio and other default params
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = None
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(3)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            # print(msg)    # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test002_NRCRecogLang_enUS(self):
        """
        Test NRC multi-language recognition en-US via inline grammar with ULaw audio yes.ulaw
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = 'yes.ulaw'
        test_audio_format = 'ulaw'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'
        test_language = 'en-US'
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=en-US")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"[0-9].+")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
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

    def test003_NRCRecogLang_esESUlaw(self):
        """
        Test NRC multi-language recognition es-ES via builtin grammar with ULaw audio 1234_es.ulaw
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = '1234_es.ulaw'
        test_audio_format = 'ulaw'
        test_language = 'es-ES'
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>1234<\/instance.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=es-ES")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
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

    def test004_NRCRecogLang_esESAlaw(self):
        """
        Test NRC multi-language recognition es-ES via builtin grammar with ALaw audio 1234_es.alaw
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio = '1234_es.alaw'
        test_audio_format = 'alaw'
        test_language = 'es-ES'
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>1234<\/instance.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data,
                                                    languageIn=test_language)
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
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test005_NRCRecogLang_esESPCM(self):
        """
        Test NRC multi-language recognition es-ES via builtin grammar with PCM audio 1234_e5.wav
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'es-ES'
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>1234<\/instance.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data,
                                                    languageIn=test_language)
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
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test006_NRCRecogLang_esUSUlaw(self):
        """
        Test NRC multi-language recognition es-US via builtin grammar with ULaw audio 1234_es.ulaw
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = '1234_es.ulaw'
        test_audio_format = 'ulaw'
        test_language = 'es-US'
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>1234<\/instance.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
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

    def test007_NRCRecogLang_esUSAlaw(self):
        """
        Test NRC multi-language recognition es-US via builtin grammar with ALaw audio 1234_es.alaw
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio = '1234_es.alaw'
        test_audio_format = 'alaw'
        test_language = 'es-US'
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>1234<\/instance.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data,
                                                    languageIn=test_language)
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
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test008_NRCRecogLang_esUSPCM(self):
        """
        Test NRC multi-language recognition es-US via builtin grammar with PCM audio 1234_e5.wav
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'es-US'
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>1234<\/instance.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data,
                                                    languageIn=test_language)
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
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test009_NRCRecogInlineGrammar_esES(self):
        """
        Test NRC multiple language recognition via inline grammar es-ES with audio input si.ulaw.raw
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio = 'si.ulaw.raw'
        test_audio_format = 'ulaw'
        test_language = 'es-ES'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"es-ES\" version=\"1.0\" root=\"si_no\"> <rule id=\"si_no\" scope=\"public\">\n<one-of>\n<item>si</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>si</SWI_literal>.+<SWI_meaning.+si.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
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
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test010_NRCRecogInlineGrammar_esUS(self):
        """
        Test NRC multiple language recognition with inline grammar es-US with audio input si.wav
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = 'si.wav'
        test_audio_format = 'pcm'
        test_language = 'es-US'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"es-US\" version=\"1.0\" root=\"si_no\"> <rule id=\"si_no\" scope=\"public\">\n<one-of>\n<item>si</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>si</SWI_literal>.+<SWI_meaning.+si.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=es-US")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"[0-9].+")

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

    def test011_NRCRecogUriGrammar_esES(self):
        """
        Test NRC multiple language recognition with uri grammar es-ES with audio input si.ulaw.raw
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio = 'si.ulaw.raw'
        test_audio_format = 'ulaw'
        test_language = 'es-ES'
        test_media_type = 'srgsxml'
        test_grammar = "uri_grammar_si_es-ES.grxml"
        test_grammar_type = "uri_grammar"
        test_grammar_uri = client.test_res_url + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>si</SWI_literal>.+<SWI_meaning.+si.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type, languageIn=test_language)
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
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test012_NRCRecogUriGrammar_esUS(self):
        """
        Test NRC multiple language recognition with uri grammar es-US with audio input si.wav
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = 'si.wav'
        test_audio_format = 'pcm'
        test_language = 'es-ES'
        test_media_type = 'srgsxml'
        test_grammar = "uri_grammar_si_es-US.grxml"
        test_grammar_type = "uri_grammar"
        test_grammar_uri = client.test_res_url + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>si</SWI_literal>.+<SWI_meaning.+si.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\""+test_grammar_uri)

        try:
            #
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

    def test013_NRCRecogLang_frCAUlaw(self):
        """
        Test NRC multi-language recognition fr-CA via builtin grammar with ULaw audio 1234_fr.ulaw.raw
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio = '1234_fr.ulaw.raw'
        test_audio_format = 'ulaw'
        test_language = 'fr-CA'
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data,
                                                    languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>1234<\/instance.+\/interpretation.+\/result>"
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

    def test014_NRCRecogLang_frCAAlaw(self):
        """
        Test NRC multi-language recognition fr-CA via builtin grammar with ALaw audio 1234_fr.alaw.raw
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio = '1234_fr.alaw.raw'
        test_audio_format = 'alaw'
        test_language = 'fr-CA'
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+><input mode.+>un deux trois quatre</input><instance>1234</instance>.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data,
                                                    languageIn=test_language)
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
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test015_NRCRecogLang_frCAPCM(self):
        """
        Test NRC multi-language recognition fr-CA via builtin grammar with PCM audio 1234_fr.wav
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio = '1234_fr.wav'
        test_audio_format = 'pcm'
        test_language = 'fr-CA'
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+><input mode.+>un deux trois quatre</input><instance>1234</instance>.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data,
                                                    languageIn=test_language)
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
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test016_NRCRecogInlineGrammar_frCA(self):
        """
        Test NRC multi-language recognition via inline grammar fr-CA and audio oui.ulaw
        Expect NRC recognize successfully
        """
        client = gRPCClient()
        #
        test_audio = 'oui.alaw.raw'
        test_audio_format = 'alaw'
        test_language = 'fr-CA'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"fr-CA\" version=\"1.0\" root=\"oui_non\"> <rule id=\"oui_non\" scope=\"public\">\n<one-of>\n<item>oui</item>\n<item>non</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>oui</SWI_literal>.+<SWI_meaning.+oui.+SWI_meaning></instance></interpretation></result>"
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

    def test017_NRCRecogUriGrammar_frCA(self):
        """
        Test NRC multiple language recognition with uri grammar fr-CA with audio input oui.wav
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = 'oui.wav'
        test_audio_format = 'pcm'
        test_language = 'fr-CA'
        test_media_type = 'srgsxml'
        test_grammar = "uri_grammar_oui_fr-CA.grxml"
        test_grammar_type = "uri_grammar"
        test_grammar_uri = client.test_res_url + test_grammar
        # print("Test grammar URI: " + test_grammar_uri + "\n")

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>oui</SWI_literal>.+<SWI_meaning.+oui.+SWI_meaning></instance></interpretation></result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value=test_grammar_uri)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\""+test_grammar_uri)

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

    def test018_NRCRecogMismatch_Lang_esES_Audio_frCA(self):
        """
        Test NRC multiple language recognition via mismatch language settings es-ES with fr-CA audio input 1234_fr.wav
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '1234_fr.wav'
        test_audio_format = 'pcm'
        test_language = 'es-ES'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"es-ES\" version=\"1.0\" root=\"si_no\"> <rule id=\"si_no\" scope=\"public\">\n<one-of>\n<item>si</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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

    def test019_NRCRecogMismatch_Lang_esUS_Audio_enUS(self):
        """
        Test NRC multiple language recognition via mismatch language settings es-US with en-US audio input 01234.ulaw
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '01234.ulaw'
        test_audio_format = 'ulaw'
        test_language = 'es-US'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"es-US\" version=\"1.0\" root=\"si_no\"> <rule id=\"si_no\" scope=\"public\">\n<one-of>\n<item>si</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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

    def test020_NRCRecogMismatch_Lang_frCA_Audio_esES(self):
        """
        Test NRC multiple language recognition via mismatch language settings fr-CA with es-ES audio input 1234_es5.wav
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'fr-CA'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"fr-CA\" version=\"1.0\" root=\"oui_non\"> <rule id=\"oui_non\" scope=\"public\">\n<one-of>\n<item>oui</item>\n<item>non</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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

    def test021_NRCRecogMismatch_Lang_enUS_Audio_esUS(self):
        """
        Test NRC multiple language recognition via mismatch language settings en-US with es-US audio input 1234_es5.wav
        Expect
        1) [Test Case] NRC recognize return SWIrec_STATUS_NO_MATCH
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check SWIrslt absent from call logs (due to NO_MATCH)
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'en-US'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, result_status="NO_MATCH")
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=en-US")
        # test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="lowconf")
        # test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RSLT", value="{SWI_literal:yes}")
        test_record_1.add_undesired_to_checklist("SWIrslt")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)
            time.sleep(1)
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

    def test022_NRCRecogInvalid_Lang(self):
        """
        Test NRC multiple language recognition via invalid language settings en-US with es-US audio input 1234_es5.wav
        Expect
        1) [Test Case] NRC recognize return SWIrec_STATUS_NO_MATCH
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check SWIrslt absent from call logs (due to NO_MATCH)
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'xx-xx'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, result_status="NO_MATCH")
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=xx-xx")
        # test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="lowconf")
        # test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RSLT", value="{SWI_literal:yes}")
        test_record_1.add_undesired_to_checklist("SWIrslt")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio,
                                                            recInit=test_recInit)
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

    def test023_NRCRecogLang_jaJPUlaw(self):
        """
        Test NRC multi-language recognition ja-JP via builtin grammar with ULaw audio 1234_jp.ulaw
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = '1234_jp.ulaw'
        test_audio_format = 'ulaw'
        test_language = 'ja-JP'
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+input mode=\"speech\">イチ ニ サン ヨン.+\/input><instance>1234<\/instance.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
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

    def test300_NRCRecogInvalid_Lang_Invalid_Format_Dot_Lowercase(self):
        """
        Test NRC language recognition via invalid language xx.xx with es-US audio input 1234_es5.wav
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'xx.xx'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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

    def test301_NRCRecogInvalid_Lang_Invalid_Format_Underscore_Lowercase(self):
        """
        Test NRC language recognition via invalid language xx_xx with es-US audio input 1234_es5.wav
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'xx_xx'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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

    def test302_NRCRecogInvalid_Lang_Invalid_Format_Dash_Uppercase(self):
        """
        Test NRC language recognition via invalid language XX-XX with es-US audio input 1234_es5.wav
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'XX-XX'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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

    def test303_NRCRecogValid_Lang_Invalid_Format_Dash_Lowercase(self):
        """
        Test NRC  language recognition via valid language invalid format en-us with es-US audio input 1234_es5.wav
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'en-us'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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

    def test304_NRCRecogValid_Lang_Invalid_Format_Dot_Lowercase(self):
        """
        Test NRC  language recognition via valid language invalid format en.us with es-US audio input 1234_es5.wav
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'en.us'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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

    def test305_NRCRecogValid_Lang_Invalid_Format_Underscore_Lowercase(self):
        """
        Test NRC language recognition via valid language invalid format en_us with es-US audio input 1234_es5.wav
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'en_us'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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

    def test306_NRCRecogValid_Lang_Invalid_Format_Dash_Uppercase(self):
        """
        Test NRC language recognition via valid language invalid format EN-US with es-US audio input 1234_es5.wav
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'EN-US'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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

    def test307_NRCRecogValid_Lang_Invalid_Format_Dot_Mixed_Case(self):
        """
        Test NRC language recognition via valid language invalid format en.US with es-US audio input 1234_es5.wav
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'en.US'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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

    def test308_NRCRecogValid_Lang_Invalid_Format_Underscore_Mixed_Case(self):
        """
        Test NRC language recognition via valid language invalid format en_US with es-US audio input 1234_es5.wav
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'en_US'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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

    def test309_NRCRecogMismatch_Lang_frCA_Audio_enUS(self):
        """
        Test NRC  language recognition via mismatch language settings fr-CA with en-US audio input 01234.ulaw
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '01234.ulaw'
        test_audio_format = 'ulaw'
        test_language = 'fr-CA'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"fr-CA\" version=\"1.0\" root=\"oui_non\"> <rule id=\"oui_non\" scope=\"public\">\n<one-of>\n<item>oui</item>\n<item>non</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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

    def test500_NRCRecogMismatch_Lang_enUS_Audio_frCA(self):
        """
        Test NRC  language recognition via mismatch language settings en-US with fr-CA audio input oui.wav
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = 'oui.wav'
        test_audio_format = 'pcm'
        test_language = 'en-US'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-US\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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

    def test501_NRCRecogValid_Lang_Invalid_Format_Inverted_Lang_Country(self):
        """
        Test NRC language recognition via valid language invalid format US-en with en-US audio input 01234.ulaw
        Expect NRC recognize return "code: 400\nmessage: "Bad Request"\ndetails: "Failed to load RecognitionResource at index (0-based): 0"
        """
        client = gRPCClient()
        #
        test_audio = '01234.ulaw'
        test_audio_format = 'ulaw'
        test_language = 'US-en'
        test_grammar_type = 'builtin'
        test_grammar_data = 'digits'
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Failed to load RecognitionResource"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data,
                                                    languageIn=test_language)
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
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            time.sleep(20)

    def test101_NRCRecogLang_enAU(self):
        """
        Test NRC multi-language recognition en-AU via inline grammar with ULaw audio yes.ulaw
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = 'yes.ulaw'
        test_audio_format = 'ulaw'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-AU\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'
        test_language = 'en-AU'
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=en-US")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"[0-9].+")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

    def test102_NRCRecogLang_enGB(self):
        """
        Test NRC multi-language recognition en-GB via inline grammar with ULaw audio yes.ulaw
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = 'yes.ulaw'
        test_audio_format = 'ulaw'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-GB\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'
        test_language = 'en-GB'
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=en-GB")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"[0-9].+")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)    
            
    def test103_NRCRecogLang_nlNL(self):
        """
        Test NRC multi-language recognition nl-NL via inline grammar with ULaw audio yes.ulaw
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = 'yes.ulaw'
        test_audio_format = 'ulaw'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"nl-NL\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'
        test_language = 'nl-NL'
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=nl-NL")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"[0-9].+")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
            
    def test104_NRCRecogLang_frFR(self):
        """
        Test NRC multi-language recognition fr-FR via inline grammar with ULaw audio yes.ulaw
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = 'yes.ulaw'
        test_audio_format = 'ulaw'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"fr-FR\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'
        test_language = 'fr-FR'
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=fr-FR")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"[0-9].+")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)            
            
    def test105_NRCRecogLang_deDE(self):
        """
        Test NRC multi-language recognition de-DE via inline grammar with ULaw audio yes.ulaw
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = 'yes.ulaw'
        test_audio_format = 'ulaw'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"de-DE\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'
        test_language = 'de-DE'
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=de-DE")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"[0-9].+")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e) 
            
    def test106_NRCRecogLang_itIT(self):
        """
        Test NRC multi-language recognition it-IT via inline grammar with ULaw audio yes.ulaw
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = 'yes.ulaw'
        test_audio_format = 'ulaw'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"it-IT\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'
        test_language = 'it-IT'
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=it-IT")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"[0-9].+")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)   
            
    def test107_NRCRecogLang_ptBR(self):
        """
        Test NRC multi-language recognition pt-BR via inline grammar with ULaw audio yes.ulaw
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = 'yes.ulaw'
        test_audio_format = 'ulaw'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"pt-BR\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'
        test_language = 'pt-BR'
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=pt-BR")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"[0-9].+")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)                       
            
    def test108_NRCRecogLang_ptPT(self):
        """
        Test NRC multi-language recognition pt-PT via inline grammar with ULaw audio yes.ulaw
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = 'yes.ulaw'
        test_audio_format = 'ulaw'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"pt-PT\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'
        test_language = 'pt-PT'
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar, mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value="swirec_language=pt-PT")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=\"[0-9].+")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)                       
                                
    def test151_NRCRecogLang_Invalide_enAU(self):
        """
        Test NRC language recognition via invalid language XX-XX with en-AU audio input 1234_es5.wav
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'XX-XX'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-AU\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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
                        
    def test152_NRCRecogLang_Invalide_enGB(self):
        """
        Test NRC language recognition via invalid language XX-XX with en-GB audio input 1234_es5.wav
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'XX-XX'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"en-GB\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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
                        
    def test153_NRCRecogLang_Invalide_nlNL(self):
        """
        Test NRC language recognition via invalid language XX-XX with nl-NL audio input 1234_es5.wav
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'XX-XX'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"nl-NL\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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
                                    
    def test154_NRCRecogLang_Invalide_frFR(self):
        """
        Test NRC language recognition via invalid language XX-XX with fr-FR audio input 1234_es5.wav
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'XX-XX'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"fr-FR\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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
                                    
    def test155_NRCRecogLang_Invalide_deDE(self):
        """
        Test NRC language recognition via invalid language XX-XX with de-DE audio input 1234_es5.wav
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'XX-XX'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"de-DE\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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
                                    
    def test156_NRCRecogLang_Invalide_itIT(self):
        """
        Test NRC language recognition via invalid language XX-XX with it-IT audio input 1234_es5.wav
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'XX-XX'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"it-IT\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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
                                    
    def test157_NRCRecogLang_Invalide_ptBR(self):
        """
        Test NRC language recognition via invalid language XX-XX with pt-BR audio input 1234_es5.wav
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'XX-XX'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"pt-BR\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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
            
    def test158_NRCRecogLang_Invalide_ptPT(self):
        """
        Test NRC language recognition via invalid language XX-XX with pt-PT audio input 1234_es5.wav
        Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        """
        client = gRPCClient()
        #
        test_audio = '1234_es5.wav'
        test_audio_format = 'pcm'
        test_language = 'XX-XX'
        test_grammar = "<?xml version=\"1.0\"?>\n<grammar xmlns=\"http://www.w3.org/2001/06/grammar\" xml:lang=\"pt-PT\" version=\"1.0\" root=\"yes_no\"> <rule id=\"yes_no\" scope=\"public\">\n<one-of>\n<item>yes</item>\n<item>no</item>\n</one-of>\n</rule>\n</grammar>\n"
        test_grammar_type = 'inline_grammar'
        test_media_type = 'srgsxml'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar,
                                                    mediaType=test_media_type, languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"
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

    def test121_NRCRecogLang_Dtmf_enUS(self):

        client = gRPCClient()

        test_dtmf = "1234"
       
        test_language = 'en-US'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'number'

        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/number.+<instance>1234<\/instance.+\/interpretation.+\/result>"

                
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            
            print(msg)  # for debug
            
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test122_NRCRecogLang_Dtmf_deDE(self):

        client = gRPCClient()

        test_dtmf = "1234"

        test_language = 'de-DE'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'number'

        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/number.+<instance>1234<\/instance.+\/interpretation.+\/result>"

        try:

            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)

            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
    def test123_NRCRecogLang_Dtmf_enAU(self):

        client = gRPCClient()

        test_dtmf = "1234"

        test_language = 'en-US'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'number'

        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/number.+<instance>1234<\/instance.+\/interpretation.+\/result>"


        try:

            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)

            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
    def test124_NRCRecogLang_Dtmf_enGB(self):

        client = gRPCClient()

        test_dtmf = "1234"

        test_language = 'en-GB'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'number'

        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/number.+<instance>1234<\/instance.+\/interpretation.+\/result>"

        try:

            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)

            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
    def test125_NRCRecogLang_Dtmf_esES(self):

        client = gRPCClient()

        test_dtmf = "1234"

        test_language = 'es-ES'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'number'

        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/number.+<instance>1234<\/instance.+\/interpretation.+\/result>"

        try:

            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)

            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
    def test126_NRCRecogLang_Dtmf_esUS(self):

        client = gRPCClient()

        test_dtmf = "1234"

        test_language = 'es-US'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'number'

        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/number.+<instance>1234<\/instance.+\/interpretation.+\/result>"

        try:

            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)

            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
    def test127_NRCRecogLang_Dtmf_frCA(self):

        client = gRPCClient()

        test_dtmf = "1234"

        test_language = 'fr-CA'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'number'

        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/number.+<instance>1234<\/instance.+\/interpretation.+\/result>"

        try:

            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)

            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
    def test128_NRCRecogLang_Dtmf_frFR(self):

        client = gRPCClient()

        test_dtmf = "1234"

        test_language = 'fr-FR'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'number'

        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/number.+<instance>1234<\/instance.+\/interpretation.+\/result>"

        try:

            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)

            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
    def test129_NRCRecogLang_Dtmf_itIT(self):

        client = gRPCClient()

        test_dtmf = "1234"

        test_language = 'it-IT'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'number'

        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/number.+<instance>1234<\/instance.+\/interpretation.+\/result>"

        try:

            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)

            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
    def test130_NRCRecogLang_Dtmf_nlNL(self):

        client = gRPCClient()

        test_dtmf = "1234"

        test_language = 'nl-NL'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'number'

        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/number.+<instance>1234<\/instance.+\/interpretation.+\/result>"

        try:

            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)

            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
    def test131_NRCRecogLang_Dtmf_ptBR(self):

        client = gRPCClient()

        test_dtmf = "1234"

        test_language = 'pt-BR'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'number'

        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/number.+<instance>1234<\/instance.+\/interpretation.+\/result>"

        try:

            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)

            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
    def test132_NRCRecogLang_Dtmf_ptPT(self):

        client = gRPCClient()

        test_dtmf = "1234"

        test_language = 'pt-PT'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'number'

        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/number.+<instance>1234<\/instance.+\/interpretation.+\/result>"

        try:

            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)

            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
                                            
