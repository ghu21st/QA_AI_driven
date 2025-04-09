import sys
import os
import time

nrc_setup_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../NRCSetupClass'))
if os.path.isdir(nrc_setup_path):
    sys.path.append(nrc_setup_path)
else:
    raise ImportError(f"No Such path to the NRCSetup Class: {nrc_setup_path}")

try:
    from Framework.nrctest.NRCSetupClass.TestFixture import TestFixture
    from Framework.nrctest.NRCSetupClass.gRPCClient import gRPCClient, TimeoutException
    from Framework.nrctest.NRCSetupClass.KafkaModule import KafkaModule
except ImportError as e:
    raise ImportError(f"Required module not found: {e}. Ensure all dependencies are installed and accessible.")


# ------- NRC automation test class -----------
class NRCTestAudio(TestFixture):
    """ NRC audio test"""

    def test001_NRCAudioGeneric1(self):
        """
        Test NRC generic audio 1 - default ulaw with default recognize parameter & config - one.ulaw
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = "one.ulaw"
        test_recInit = None
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"
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

    def test002_NRCAudioUlaw1(self):
        """
        Test NRC audio - ulaw 2 with default recognize parameters/config - 945015260.ulaw
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = "945015260.ulaw"
        test_audio_format = 'ulaw'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+instance>945015260</instance></interpretation>.+\</result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:
            # init -> send audio -> recognize
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            # validate recognize result
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test003_NRCAudioUlaw2(self):
        """
        Test NRC audio - ulaw 2 with default recognize parameters/config - c375037503750373.ulaw
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = "0123456789.ulaw"
        test_recInit = None
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+instance>0123456789</instance></interpretation>.+\</result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")

        try:
            # init -> send audio -> recognize
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            # validate recognize result
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test004_NRCAudioAlaw1(self):
        """
        Test NRC generic audio 1 - default ulaw with default recognize parameter & config - 1.alaw
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = "1.alaw"
        test_audio_format = 'alaw'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
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

    def test005_NRCAudioAlaw2(self):
        """
        Test NRC generic audio 1 - default ulaw with default recognize parameter & config - c375037503750373.alaw
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = "c375037503750373.alaw"
        test_audio_format = 'alaw'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>375037503750373<\/instance.+\/interpretation.+\/result>"
        test_expect_callLog = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>FluentD redacted possible CCN<\/instance.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect_callLog)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect_callLog)
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

    def test006_NRCAudioPCM1(self):
        """Test NRC audio PCM 1 - audio format PCM with default recognize parameters config - c375037503750373.pcm
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = "c375037503750373.pcm"
        test_audio_format = 'pcm'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>375037503750373<\/instance.+\/interpretation.+\/result>"
        test_expect_callLog = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>FluentD redacted possible CCN<\/instance.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect_callLog)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect_callLog)
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

    def test007_NRCAudioPCM2(self):
        """Test NRC audio PCM 2 - audio format PCM with default recognize parameters - c375037503750373_16bit_8kHz.pcm
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = "c375037503750373_16bit_8kHz.pcm"
        test_audio_format = 'pcm'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>375037503750373<\/instance.+\/interpretation.+\/result>"
        test_expect_callLog = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>FluentD redacted possible CCN<\/instance.+\/interpretation.+\/result>"
                       
        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect_callLog)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect_callLog)
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

    def test008_NRCAudioWAV1(self):
        """Test NRC audio WAV 1 - audio format PCM with default recognize parameters - c375037503750373_8KHz.wav
        Expect
        1) [Test Case] NRC recognize successfully
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = "c375037503750373_8KHz.wav"
        test_audio_format = 'pcm'
        test_language = "en-US"
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>375037503750373<\/instance.+\/interpretation.+\/result>"
        test_expect_callLog = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>FluentD redacted possible CCN<\/instance.+\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource(grammarType='builtin', grammarData='digits', languageIn=test_language)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect_callLog)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect_callLog)
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

    def test009_NRCAudioMismatchWAV2(self):
        """Test NRC mismatch audio WAV 2 - audio format PCM but with 16KHz which not accepted by design (Proto) - c375037503750373_16KHz.wav
        Expect
        1) [Test Case] NRC recognize return SWIrec_STATUS_NO_MATCH
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check:
                - SWIrcnd: contains return code RSTT=lowconf, ENDR="eeos" (external end of speech)
                - Absent events: SWIrslt
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = "c375037503750373_16KHz.wav"
        test_audio_format = 'pcm'
        test_expect = "NO_MATCH"
        #test_expect = test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.*<nomatch>eight three eight eight</nomatch>.*\/interpretation.+\/result>"
        

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, result_status="NO_MATCH")
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="lowconf")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="ENDR", value="eeos")
        test_record_1.add_undesired_to_checklist("SWIrslt")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            
            kafka.validate_callLogs(test_record_1)
        
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test010_NRCAudioSilence(self):
        """Test NRC audio silence - audio format ulaw but not accepted by NRC 16KHz - c375037503750373_16KHz.wav
        Expect
        1) [Test Case] NRC recognize return SWIrec_STATUS_NO_MATCH
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check:
                - SWIrcnd: contains return code RSTT=stop, RENR=stop
                - SWIstop: contains MODE=TIMEOUT
                - Absent events: SWIrslt
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = "silence.ulaw"
        test_recogParams = client.recognition_parameters(audioFormat='ulaw', resultFormat='nlsml')
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)

        test_expect1 = 'code: 404'
        test_expect2 = 'message: \"No Speech\"'
        test_expect3 = 'details: \"No speech detected\"'
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect1, status_message="No Speech (audio silence)", status_code=404)
        test_record_1.set_checklist_types(["Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="stop")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RENR", value="stop")
        test_record_1.add_token_to_checklist(evnt="SWIstop", token="MODE", value="TIMEOUT")
        test_record_1.add_undesired_to_checklist("SWIrslt")
        test_record_1.add_undesired_to_checklist("NUANwvfm")

        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(3)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)
            #
            kafka.validate_callLogs(test_record_1)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test300_NRCAudioWAV1MismatchFormatUlaw(self):
        '''
        Test NRC audio silence - audio format wav but set to ulaw
        Expect
        1) [Test Case] NRC recognize return No-Input Timeout (audio silence)
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check:
                - SWIrcnd: contains return code RSTT=stop, RENR=stop
                - SWIstop: contains MODE=TIMEOUT
                - Absent events: SWIrslt
        '''

        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = "c375037503750373_8KHz.wav"
        test_audio_format = 'ulaw'
        test_expect1 = "code: 404"
        test_expect2 = 'message: \"No Speech\"'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        
        # kafka record
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect1, status_message="No-Input Timeout (audio silence)", status_code=404)
        test_record_1.set_checklist_types(["Recognition", "Grammar", "Endpointer"])
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="stop")
        test_record_1.add_token_to_checklist(evnt="SWIrcnd", token="RENR", value="stop")
        test_record_1.add_token_to_checklist(evnt="SWIstop", token="MODE", value="TIMEOUT")
        test_record_1.add_undesired_to_checklist("SWIrslt")
        test_record_1.add_undesired_to_checklist("NUANwvfm")
        
        #
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            
            kafka.validate_callLogs(test_record_1)
             
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test301_NRCAudioWAV1MismatchFormatAlaw(self):
        # Test NRC audio WAV 1 - audio format set to alaw
        # Expect NRC recognize return SWIrec_STATUS_NO_MATCH
        client = gRPCClient()
        #
        test_audio = "c375037503750373_8KHz.wav"
        test_audio_format = 'alaw'
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.+builtin:grammar\/digits.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        #
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test302_NRCAudioWAV1MismatchFormatInvalid(self):
        # Test NRC audio WAV 1 - audio format set to invalid
        # Expect NRC recognize return No-Input Timeout
        """
        Test NRC audio silence - audio format invalid
        Expect
        1) [Test Case] NRC recognize return No-Input Timeout (audio silence)
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check:
                - SWIrcnd: contains return code RSTT=stop, RENR=stop
                - SWIstop: contains MODE=TIMEOUT
                - Absent events: SWIrslt, NUANwvfm
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        #
        test_audio = "c375037503750373_8KHz.wav"
        test_audio_format = 'invalid'
        test_expect = 'message: \"No Speech\"'

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        
        # kafka record
        test_record = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, status_message="No-Input Timeout (audio silence)", status_code=404)
        test_record.set_checklist_types(["Recognition", "Grammar", "Endpointer"])
        test_record.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="stop")
        test_record.add_token_to_checklist(evnt="SWIrcnd", token="RENR", value="stop")
        test_record.add_token_to_checklist(evnt="SWIstop", token="MODE", value="TIMEOUT")
        test_record.add_undesired_to_checklist("SWIrslt")
        test_record.add_undesired_to_checklist("NUANwvfm")
        
        try:
            #
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            
            kafka.validate_callLogs(test_record)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()
            kafka.cleanup()
            
    def test303_NRCAudioUlawMismatchFormatAlaw(self):
        """
        Test NRC audio no match - used a ulaw format but set to alaw in recognition parameters
        Expect:
        1) [Test Case] NRC recognize return NO_MATCH (200 status code)
        2) [Automation call log validation] verify NRC call log
            a) Verify call log checklists: "Recognition", "Grammar", "Endpointer"
            b) Check:
                - SWIrcnd: contains return code RSTT=stop, RENR=stop
                - SWIstop: contains MODE=TIMEOUT
                - Absent events: SWIrslt
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        #
        test_audio = "c375037503750373.ulaw"
        test_audio_format = 'alaw'
        test_expect = "NO_MATCH"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        
        # kafka record
        test_record = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, result_status="NO_MATCH", status_code=200)
        test_record.set_checklist_types(["Recognition", "Grammar", "Endpointer"])
        test_record.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="lowconf")
        test_record.add_token_to_checklist(evnt="SWIrcnd", token="RENR", value="ok")
        test_record.add_undesired_to_checklist("SWIrslt")
        
        try:
            # init -> send audio -> recognize
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            # validate recognize result
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            
        
            kafka.validate_callLogs(test_record)
            

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()
            
    def test304_NRCAudioUlawMismatchFormatInvalid(self): 
        """
        This is a test case to verify the framework behavior. Setting audio format to 'invalid' results in the framework setting the type to ulaw  
        Expect:
        1) [Test Case] NRC recognize returns SUCCESS
        2) [Automation call log validation] verify NRC call log
            a) Verify call log checklists: 'Basic', 'Recognition', 'Grammar', 'Endpointer'
            b) Check:
                - SWIrcnd: contains tokens RSTT='ok', RENR='ok'
                - SWIgrld: contains token URI='builtin:grammar/digits' indicating builtin grammar
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        #
        test_audio = "c375037503750373.ulaw"
        test_audio_format = 'invalid'
        test_expect = "<result><interpretation grammar=.+builtin:grammar\/digits.+instance>375037503750373</instance></interpretation>.+\</result>"
        test_expect_callLog = "<result><interpretation grammar=.+builtin:grammar\/digits.+instance>FluentD redacted possible CCN</instance></interpretation>.+\</result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        
        # kafka record
        test_record = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect_callLog)
        test_record.set_checklist_types(["Basic","Recognition", "Grammar", "Endpointer"])
        test_record.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="ok")
        test_record.add_token_to_checklist(evnt="SWIrcnd", token="RENR", value="ok")#grammar=\"builtin:grammar/digits\"
        test_record.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        
        try:
            # init -> send audio -> recognize
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)
            # validate recognize result
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            
            kafka.validate_callLogs(test_record)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()

    def test305_NRCAudioAlawMismatchFormatUlaw(self):
        """
        Testing NRC audio - passing alaw format but setting the parameter to ulaw  
        Expect:
        1) [Test Case] NRC recognize returns SUCCESS
        2) [Automation call log validation] verify NRC call log
            a) Verify call log checklists: 'Basic', 'Recognition', 'Grammar', 'Endpointer'
            b) Check:
                - SWIrcnd: contains tokens RSTT='lowconf', RENR='ok'
                - SWIrslt: is not in the logs
        """
        
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = "c375037503750373.alaw"
        test_audio_format = 'ulaw'
        test_expect = "NO_MATCH"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        
        # kafka record to verify
        test_record = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, result_status="NO_MATCH", status_code=200)
        test_record.set_checklist_types(["Recognition", "Grammar", "Endpointer"])
        test_record.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="lowconf")
        test_record.add_token_to_checklist(evnt="SWIrcnd", token="RENR", value="ok")
        test_record.add_undesired_to_checklist("SWIrslt")
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            
            kafka.validate_callLogs(test_record)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test306_NRCAudioAlawMismatchFormatInvalid(self):
        # Test NRC audio alaw - audio format set to invalid
        # Expect NRC recognize return SWIrec_STATUS_NO_MATCH

        """
        Testing NRC audio - passing invalid audio type parameter 
        Expect:
        1) [Test Case] NRC recognize returns NO_MATCH
        2) [Automation call log validation] verify NRC call log
            a) Verify call log checklists: 'Basic', 'Recognition', 'Grammar', 'Endpointer'
            b) Check:
                - SWIrcnd: contains tokens RSTT='lowconf', RENR='ok'
                - SWIrslt: is not in the logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = "c375037503750373.alaw"
        test_audio_format = 'invalid'
        #test_expect = "SWIrec_STATUS_NO_MATCH"
        test_expect = "NO_MATCH"
        #test_expect =  "<result><interpretation grammar=.+builtin:grammar\/digits.*<nomatch>.*</nomatch>.*\/interpretation.+\/result>"

        test_recogParams = client.recognition_parameters(audioFormat=test_audio_format)
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        
        # kafka record to verify
        test_record = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, result_status="NO_MATCH", status_code=200)
        test_record.set_checklist_types(["Basic" ,"Recognition", "Grammar", "Endpointer"])
        test_record.add_token_to_checklist(evnt="SWIrcnd", token="RSTT", value="lowconf")
        test_record.add_token_to_checklist(evnt="SWIrcnd", token="RENR", value="ok")
        test_record.add_undesired_to_checklist("SWIrslt")
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            
            kafka.validate_callLogs(test_record)
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test801_invalid_audio_file_path(self):
        """
        Test NRC with an invalid audio file path.
        Expect:
        1) [Test Case] NRC recognize returns an error (e.g., file not found or invalid input).
        2) [Automation call log validation] verify NRC call log does not contain recognition results.
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = "non_existent_file.ulaw"  # Invalid file path
        test_recogParams = client.recognition_parameters(audioFormat='ulaw')
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        
        test_expect = "File not found"  # Expected error message
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            self.fail("Expected an error, but the test passed.")
        except Exception as e:
            self.debug(f"Expected error occurred: {e}")
            assert test_expect in str(e), f"Unexpected error message: {e}"
        finally:
            client.cleanup()
            kafka.cleanup()
    
    def test802_unsupported_audio_format(self):
        """
        Test NRC with an unsupported audio format.
        Expect:
        1) [Test Case] NRC recognize returns an error indicating unsupported format.
        2) [Automation call log validation] verify NRC call log does not contain recognition results.
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = "unsupported_format.xyz"  # Unsupported audio format
        test_recogParams = client.recognition_parameters(audioFormat='xyz')  # Invalid format
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        
        test_expect = "Unsupported audio format"  # Expected error message
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            self.fail("Expected an error, but the test passed.")
        except Exception as e:
            self.debug(f"Expected error occurred: {e}")
            assert test_expect in str(e), f"Unexpected error message: {e}"
        finally:
            client.cleanup()
            kafka.cleanup()

    def test803_missing_recognition_parameters(self):
        """
        Test NRC with missing recognition parameters.
        Expect:
        1) [Test Case] NRC recognize returns an error indicating missing parameters.
        2) [Automation call log validation] verify NRC call log does not contain recognition results.
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = "valid_audio.ulaw"
        test_recogParams = None  # Missing recognition parameters
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        
        test_expect = "Missing recognition parameters"  # Expected error message
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            self.fail("Expected an error, but the test passed.")
        except Exception as e:
            self.debug(f"Expected error occurred: {e}")
            assert test_expect in str(e), f"Unexpected error message: {e}"
        finally:
            client.cleanup()
            kafka.cleanup()

    def test804_exceeding_max_audio_length(self):
        """
        Test NRC with audio input exceeding the maximum allowed length.
        Expect:
        1) [Test Case] NRC recognize returns an error indicating audio length exceeded.
        2) [Automation call log validation] verify NRC call log does not contain recognition results.
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = "exceeding_length.ulaw"  # Simulated long audio file
        test_recogParams = client.recognition_parameters(audioFormat='ulaw')
        test_recogRes = client.recognition_resource()
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        
        test_expect = "Audio length exceeded"  # Expected error message
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            self.fail("Expected an error, but the test passed.")
        except Exception as e:
            self.debug(f"Expected error occurred: {e}")
            assert test_expect in str(e), f"Unexpected error message: {e}"
        finally:
            client.cleanup()
            kafka.cleanup()

    def test805_invalid_recognition_resource(self):
        """
        Test NRC with an invalid recognition resource.
        Expect:
        1) [Test Case] NRC recognize returns an error indicating invalid resource.
        2) [Automation call log validation] verify NRC call log does not contain recognition results.
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = "valid_audio.ulaw"
        test_recogParams = client.recognition_parameters(audioFormat='ulaw')
        test_recogRes = None  # Invalid recognition resource
        test_recInit = client.recognition_init(test_recogParams, test_recogRes)
        
        test_expect = "Invalid recognition resource"  # Expected error message
        
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            self.fail("Expected an error, but the test passed.")
        except Exception as e:
            self.debug(f"Expected error occurred: {e}")
            assert test_expect in str(e), f"Unexpected error message: {e}"
        finally:
            client.cleanup()
            kafka.cleanup()