import sys
import os
import time

if os.path.isdir(os.path.join(os.path.dirname(__file__), '../../', './NRCSetupClass')):
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../', './NRCSetupClass'))
else:
    raise ImportError("No Such path to the NRCSetup Class")

from Framework.nrctest.NRCSetupClass.TestFixture import TestFixture
from Framework.nrctest.NRCSetupClass.gRPCClient import gRPCClient, TimeoutException
from Framework.nrctest.NRCSetupClass.KafkaModule import KafkaModule

# ------- NRC automation test class -----------
class NRCTestDtmf(TestFixture):
            
    def test001_NRCDtmfGeneric1(self):

        client = gRPCClient()

        test_dtmf = "1"
       
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"

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

    def test002_NRCDtmf_resultFormat_nlsml(self):

        client = gRPCClient()

        test_dtmf = "12"
        
        test_result_format = 'emma'
        test_expect = "<?xml.+<emma:emma.+<emma:interpretation.+emma:tokens=.+one.+emma:interpretation>.+emma:emma>"

        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>12<\/instance.+\/interpretation.+\/result>"
        
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            
            #print(msg)  # for debug
            
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test003_NRCDtmf_resultFormat_emma(self):

        client = gRPCClient()

        test_dtmf = "12"
        
        test_result_format = 'emma'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters(resultFormat=test_result_format)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<?xml.+<emma:emma.+<emma:interpretation.+emma:tokens=.+12.+emma:interpretation>.+emma:emma>"
        
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)

            #print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test004_NRCDtmf_Number(self):

        client = gRPCClient()

        test_dtmf = "1234"
       
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'number'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/number.+<instance>1234<\/instance.+\/interpretation.+\/result>"
        
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            
            #print(msg)  # for debug
            
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test005_NRCDtmf_dtmf_then_audio(self):
        """
        Test NRC recognition dtmf followed by NRC recognition audio
        Expect 
        1) [Test Case] NRC recognition requests successful
        """
        client = gRPCClient()

        # Recognition request 1: dtmf
        test_dtmf1 = "1234"
        test_grammar_type1 = 'builtin:dtmf'
        test_grammar_data1 = 'number'
        test_recogParams1 = client.dtmfrecognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_dtmfrecInit1 = client.dtmfrecognition_init(test_recogParams1, test_recogRes1)
        test_expect1 = "<result><interpretation grammar=.+builtin:dtmf\/number.+<instance>1234<\/instance.+\/interpretation.+\/result>"
        
        # Recognition request 2: audio
        test_audio2 = "945015260.ulaw"
        test_grammar_type2 = 'builtin'
        test_grammar_data2 = 'digits'        
        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_data2)
        test_recInit2 = client.recognition_init(test_recogParams2, test_recogRes2)
        test_expect2 = "<result><interpretation grammar=.+builtin:grammar\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"

        try:            
            test_result1 = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf1, dtmfrecInit=test_dtmfrecInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)

            msg = "Test result1:\n" + test_result1 + "\n"
            msg += "Test result2:\n" + test_result2 + "\n"
            self.debug(msg)
            
            print(msg)  # for debug
            
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test006_NRCDtmf_dtmf_then_dtmf(self):
        """
        Test NRC recognition dtmf followed by NRC recognition dtmf
        Expect 
        1) [Test Case] NRC recognition requests successful
        """

        client = gRPCClient()

        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'number'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        
        # Recognition request 1: dtmf
        test_dtmf1 = "1234"
        test_expect1 = "<result><interpretation grammar=.+builtin:dtmf\/number.+<instance>1234<\/instance.+\/interpretation.+\/result>"
        
        # Recognition request 2: dtmf
        test_dtmf2 = "56786"
        test_expect2 = "<result><interpretation grammar=.+builtin:dtmf\/number.+<instance>56786<\/instance.+\/interpretation.+\/result>"
        try:
            test_result1 = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf1, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            test_result2 = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf2, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)

            msg = "Test result:\n" + test_result1 + "\n"
            msg += "Test result:\n" + test_result2 + "\n"
            self.debug(msg)
            
            print(msg)  # for debug
            
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
          
    def test007_NRCDtmf_minlength_No_Match(self):

        client = gRPCClient()

        test_dtmf = "1#9"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits?minlenght=4'
        test_dtmfTermChar= '*'
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "NO_MATCH"
        
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            
            #print(msg)  # for debug
            
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
    def test008_NRCDtmf_maxlength_1_No_Match(self):

        client = gRPCClient()

        test_dtmf = "15#9"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits?maxlenght=1'
        test_dtmfTermChar= '*'
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "NO_MATCH"
        
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

    def test009_NRCDtmf_maxlength_2_No_Match(self):

        client = gRPCClient()

        test_dtmf = "153#9"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits?maxlenght=2'
        test_dtmfTermChar= '*'
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "NO_MATCH"
        
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            
            #print(msg)  # for debug
            
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
    def test0010_NRCDtmf_No_Match(self):

        client = gRPCClient()

        test_dtmf = "1539"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar= '1'
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "NO_MATCH"
        
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            
            #print(msg)  # for debug
            
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0011_NRCDtmf_Term_Char_hash(self):

        client = gRPCClient()

        test_dtmf = "12#9"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        
        test_dtmfTermChar= '#'
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>12<\/instance.+\/interpretation.+\/result>"
        
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            
            #print(msg)  # for debug
            
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0012_NRCDtmf_Term_Char_star(self):

        client = gRPCClient()

        #test_dtmf = "124567890123777777777777777777777"
        test_dtmf = "129*5"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar= '*'
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>129<\/instance.+\/interpretation.+\/result>"
        
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

    def test0013_NRCDtmf_Term_Char_digit_1(self):

        client = gRPCClient()

        test_dtmf = "2915"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar= '1'
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>29<\/instance.+\/interpretation.+\/result>"
        
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

    def test0014_NRCDtmf_Term_Char_digit_2(self):

        client = gRPCClient()

        test_dtmf = "1295"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar= '2'
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"
        
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
            
    def test0015_NRCDtmf_Term_Char_digit_3(self):

        client = gRPCClient()

        test_dtmf = "1244395"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar= '3'
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1244<\/instance.+\/interpretation.+\/result>"
        
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
            
    def test0016_NRCDtmf_Term_Char_digit_4(self):

        client = gRPCClient()

        #test_dtmf = "124567890123777777777777777777777"
        test_dtmf = "12954"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar= '4'
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1295<\/instance.+\/interpretation.+\/result>"
        
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
            
    def test0017_NRCDtmf_Term_Char_digit_5(self):

        client = gRPCClient()

        #test_dtmf = "124567890123777777777777777777777"
        test_dtmf = "4651295"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar= '5'
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>46<\/instance.+\/interpretation.+\/result>"
        
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
            
    def test0018_NRCDtmf_Term_Char_digit_6(self):

        client = gRPCClient()
        test_dtmf = "7865"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar= '6'
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>78<\/instance.+\/interpretation.+\/result>"
        
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            
            #print(msg)  # for debug
            
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0019_NRCDtmf_Term_Char_digit_7(self):

        client = gRPCClient()

        test_dtmf = "124567890123777777777777777777777"
        test_dtmf = "668795"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar= '7'
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>668<\/instance.+\/interpretation.+\/result>"
        
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
            
    def test0020_NRCDtmf_Term_Char_digit_8(self):

        client = gRPCClient()

        test_dtmf = "668795"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar= '8'
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>66<\/instance.+\/interpretation.+\/result>"
        
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

    def test0021_NRCDtmf_Term_Char_digit_9(self):

        client = gRPCClient()

        test_dtmf = "668795"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar= '9'
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>6687<\/instance.+\/interpretation.+\/result>"
        
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

    def test0022_NRCDtmf_Term_Char_Invalid1(self):

        client = gRPCClient()

        test_dtmf = "129*5"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar= '%'
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"The dtmf_term_char parameter is out of range."
        
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            
            time.sleep(1)
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

    def test0023_NRCDtmf_Term_Char_Invalid2(self):

        client = gRPCClient()

        #test_dtmf = "124567890123777777777777777777777"
        test_dtmf = "129*5"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar= '@'
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"The dtmf_term_char parameter is out of range."
        
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            
            time.sleep(1)
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

    def test0024_NRCDtmf_no_input_timeout(self):

        client = gRPCClient()

        #test_dtmf = "124567890123777777777777777777777"
        test_dtmf = " "
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect1 = "code: 408"
        test_expect2 = 'message: \"Audio timeout\"'
        test_expect3 = "details: \"No DTMF received"
        
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            
            #print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0025_NRCDtmf_no_input_timeout_2(self):

        client = gRPCClient()

        #test_dtmf = "124567890123777777777777777777777"
        test_dtmf = "P"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect1 = "code: 408"
        test_expect2 = 'message: \"Audio timeout\"'
        test_expect3 = "details: \"No DTMF received"
        
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            
            #print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0026_NRCDtmf_no_input_timeout_Invalid(self):

        client = gRPCClient()

        test_dtmf = "1234544444448888888888888888888888888#88888888"
        test_noInputTimeout = -80
        test_dtmfTermChar= '#'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        
        test_recogParams = client.dtmfrecognition_parameters(noInputTimeout=test_noInputTimeout,dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = 'details: \"The no_input_timeout_ms parameter is out of range.*\"'
        
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            
            #print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect3)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            
    def test0027_NRCDtmf_no_input_timeout_disabled(self):

        client = gRPCClient()

        test_dtmf = "486"
        test_noInputTimeout = 0
        #test_dtmfTermChar= '#'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        
        test_recogParams = client.dtmfrecognition_parameters(noInputTimeout=test_noInputTimeout)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>486<\/instance.+\/interpretation.+\/result>"
        
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            
            #print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0028_NRCDtmf_no_input_timeout_ok(self):

        client = gRPCClient()

        test_dtmf = "56789123"
        test_noInputTimeout = 500
        #test_dtmfTermChar= '#'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        
        test_recogParams = client.dtmfrecognition_parameters(noInputTimeout=test_noInputTimeout)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>56789123<\/instance.+\/interpretation.+\/result>"
        
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            
            #print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0029_NRCDtmf_no_input_timeout_Invalid_2(self):

        client = gRPCClient()

        test_dtmf = "1234544444448888888888888888888888888#88888888"
        test_noInputTimeout = 2147483649
        #test_dtmfTermChar= '#'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        
        
        test_expect = "Value out of range: 2147483649"
        
        try:
            
           test_recogParams = client.dtmfrecognition_parameters(noInputTimeout=test_noInputTimeout)
           test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        
            
        except (AssertionError, TimeoutException, Exception) as e:
            msg = "\nFound exception!\n" + str(e)
            # print(msg)
            if self.assertRecognitionResult(inputToCheck=str(e), expectResult=test_expect):
                msg = "Test passed. Expected: \n" + msg + "\n"
                print(msg)
            else:
                self.fail(e)

    def test0030_NRCDtmf_Term_Char_timeout_0(self):

        client = gRPCClient()

        #test_dtmf = "124567890123777777777777777777777"
        test_dtmf = "12954"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar= '4'
        test_dtmfTermTimeout= 0
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar,dtmfTermTimeout=test_dtmfTermTimeout)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1295<\/instance.+\/interpretation.+\/result>"
        
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

    def test0031_NRCDtmf_Term_Char_timeout_5000(self):

        client = gRPCClient()

        #test_dtmf = "124567890123777777777777777777777"
        test_dtmf = "12954"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar= '4'
        test_dtmfTermTimeout= 5000
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar,dtmfTermTimeout=test_dtmfTermTimeout)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1295<\/instance.+\/interpretation.+\/result>"
        
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

    def test0032_NRCDtmf_Term_Char_Invalid1(self):

        client = gRPCClient()

        test_dtmf = "12954"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar= '4'
        test_dtmfTermTimeout= -10
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar,dtmfTermTimeout=test_dtmfTermTimeout)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"The dtmf_term_timeout_ms parameter is out of range."
        
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            
            time.sleep(1)
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

    def test0033_NRCDtmf_Term_Char_Invalid2(self):

        client = gRPCClient()

        test_dtmf = "12954"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar= '4'
        test_dtmfTermTimeout= -2
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar,dtmfTermTimeout=test_dtmfTermTimeout)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"The dtmf_term_timeout_ms parameter is out of range."
        
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            
            time.sleep(1)
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

    def test0034_NRCDtmf_Interdigit_OutofRange(self):

        client = gRPCClient()

        test_dtmf = "12954"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfInterdigitTimeout = -80
        test_recogParams = client.dtmfrecognition_parameters(dtmfInterdigitTimeout=test_dtmfInterdigitTimeout)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"The dtmf_interdigit_timeout_ms parameter is out of range.*"

        try:

            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)

            time.sleep(1)
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

    def test0035_NRCDtmf_Interdigit_Max(self):

        client = gRPCClient()

        test_dtmf = "12954"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfInterdigitTimeout = 2147483647
        test_recogParams = client.dtmfrecognition_parameters(dtmfInterdigitTimeout=test_dtmfInterdigitTimeout)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>12954<\/instance.+\/interpretation.+\/result>"

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

    def test0036_NRCDtmf_Interdigit_Min(self):

        client = gRPCClient()

        test_dtmf = "12954"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfInterdigitTimeout = -1
        test_recogParams = client.dtmfrecognition_parameters(dtmfInterdigitTimeout=test_dtmfInterdigitTimeout)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>12954<\/instance.+\/interpretation.+\/result>"

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

    def test0037_NRCDtmf_Interdigit1(self):

        client = gRPCClient()

        test_dtmf = "54321"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfInterdigitTimeout = 1
        test_recogParams = client.dtmfrecognition_parameters(dtmfInterdigitTimeout=test_dtmfInterdigitTimeout)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>5<\/instance.+\/interpretation.+\/result>"

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

    def test0038_NRCDtmf_Interdigit2(self):
        # This case timeout settings tested in different Kubernetes cluster may have different results (such as NRC on AKS and NRC on local QA cluster).
        # Test case 0037 & 0039 showed different timeout value result is good enough.
        # Skipped/comments this case for now.

        msg = "\nSkip test case:"
        msg += "\nThis case timeout settings tested in different Kubernetes cluster may have different results (such as NRC on AKS and NRC on local QA cluster)."
        msg += "\nTest case 0037 & 0039 showed different timeout value result is good enough."
        msg += "\nSkipped/comments this case for now."
        print(msg)        
        self.skipTest("")
        ######

        client = gRPCClient()

        test_dtmf = "54321"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfInterdigitTimeout = 1000
        test_recogParams = client.dtmfrecognition_parameters(dtmfInterdigitTimeout=test_dtmfInterdigitTimeout)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>54<\/instance.+\/interpretation.+\/result>"

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

    def test0039_NRCDtmf_Interdigit3(self):

        client = gRPCClient()

        test_dtmf = "54321"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfInterdigitTimeout = 2500
        test_recogParams = client.dtmfrecognition_parameters(dtmfInterdigitTimeout=test_dtmfInterdigitTimeout)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>54321<\/instance.+\/interpretation.+\/result>"

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

    def test0040_NRCDtmf_Interdigit_Termchar_Used(self):

        client = gRPCClient()

        test_dtmf = "668795"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar = '9'
        test_dtmfInterdigitTimeout = 5000
        test_recogParams = client.dtmfrecognition_parameters(dtmfInterdigitTimeout=test_dtmfInterdigitTimeout, dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>6687<\/instance.+\/interpretation.+\/result>"

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

    def test0041_NRCDtmf_Interdigit_Termchar_Unused(self):

        client = gRPCClient()

        test_dtmf = "668795"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar = '9'
        test_dtmfInterdigitTimeout = 10
        test_recogParams = client.dtmfrecognition_parameters(dtmfInterdigitTimeout=test_dtmfInterdigitTimeout, dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>6<\/instance.+\/interpretation.+\/result>"

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

    def test042_NRCDtmf_TwoDTMF_Noactivity_between(self):
        
        client = gRPCClient()

        test_dtmf = "1                                      2"
       
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>12<\/instance.+\/interpretation.+\/result>"

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

    def test043_NRCDtmf_MultipleDTMF_Noactivity_between(self):
        client = gRPCClient()

        test_dtmf = "1                            2                            3"
       
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>123<\/instance.+\/interpretation.+\/result>"

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
            

    def test0101_NRCDtmf_long_duration(self):

        client = gRPCClient()

        test_dtmf = "                       68"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar= '25'
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect1 = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>68<\/instance.+\/interpretation.+\/result>"
        test_expect2 = r"first_audio_to_start_of_speech_ms: \d{5}"
        
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            
            print(msg)  # for debug
            
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect2)
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0102_NRCDtmf_boolean(self):
        client = gRPCClient()

        test_dtmf = "1"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'boolean'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/boolean.+<instance>true<\/instance.+\/interpretation.+\/result>"

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

    def test0103_NRCDtmf_grammar_creditcard(self):
        client = gRPCClient()

        test_dtmf = '4125169977837959'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'creditcard'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/creditcard.+<instance>4125169977837959<\/instance.+\/interpretation.+\/result>"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test01031_NRCDtmf_grammar_creditcard_WRONG_TYPE(self):
        client = gRPCClient()

        test_dtmf = '3125169977837959'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'creditcard?typesallowed=visa'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "NO_MATCH"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test0104_NRCDtmf_grammar_date(self):
        client = gRPCClient()

        test_dtmf = '20230420'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'date'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/date.+<instance>20230420<\/instance.+\/interpretation.+\/result>"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test01041_NRCDtmf_grammar_date_LESS_MIN(self):
        client = gRPCClient()

        test_dtmf = '20090101'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'date?minallowed=20100101'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "NO_MATCH"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test0105_NRCDtmf_grammar_time(self):
        client = gRPCClient()

        test_dtmf = '2000'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'time'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/time.+<instance>2000h<\/instance.+\/interpretation.+\/result>"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test01051_NRCDtmf_grammar_time_OVER_MAX(self):
        client = gRPCClient()

        test_dtmf = '2000'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'time?maxallowed=1200'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "NO_MATCH"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)            
        finally:
            client.cleanup()

    def test0106_NRCDtmf_grammar_currency(self):
        client = gRPCClient()

        test_dtmf = '20*00'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'currency'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/currency.+<instance>USD20.00<\/instance.+\/interpretation.+\/result>"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test0107_NRCDtmf_grammar_currency_frCA(self):
        client = gRPCClient()

        test_language = 'fr-CA'
        test_dtmf = '20*00'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'currency'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/currency.+<instance>20.00<\/instance.+\/interpretation.+\/result>"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test0108_NRCDtmf_grammar_postcode(self):
        client = gRPCClient()

        test_dtmf = '91356'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'postcode'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/postcode.+<instance>91356<\/instance.+\/interpretation.+\/result>"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test0109_NRCDtmf_grammar_socialsecurity(self):
        client = gRPCClient()

        test_dtmf = '601061777'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'socialsecurity'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/socialsecurity.+<instance>601061777<\/instance.+\/interpretation.+\/result>"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test0110_NRCDtmf_grammar_phone(self):
        client = gRPCClient()

        test_dtmf = '5149047800'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'phone'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/phone.+<instance>5149047800<\/instance.+\/interpretation.+\/result>"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test0111_NRCDtmf_grammar_ccexpdate(self):
        """
        There is an issue and tested support the MMYYYY for special case only, like 122023
        """
        client = gRPCClient()

        test_dtmf = '102023'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'ccexpdate'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/ccexpdate.+<instance>20231031<\/instance.+\/interpretation.+\/result>"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        finally:
            client.cleanup()

    def test0112_NRCDtmf_secure_context_level_open(self):
        """
        """
        client = gRPCClient()
        
        test_dtmf = '945015260'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        
        test_secureContextLevel = 'OPEN'
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"
        test_recogParams = client.dtmfrecognition_parameters(secureContextLevel=test_secureContextLevel)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(dtmfrecogParam=test_recogParams, recogRes=test_recogRes)
    
        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            msg = "Test recognition result 1: \n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
     
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()
 
    def test0113_NRCDtmf_secure_context_level_suppress(self):
        """
        """
        client = gRPCClient()
         
        test_dtmf = '945015260'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        
        test_secureContextLevel = 'SUPPRESS'
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>945015260<\/instance.+\/interpretation.+\/result>"
        test_recogParams = client.dtmfrecognition_parameters(secureContextLevel=test_secureContextLevel)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(dtmfrecogParam=test_recogParams, recogRes=test_recogRes)
         
        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            msg = "Test recognition result 1: \n" + test_result + "\n"
            self.debug(msg)
            print(msg)  # for debug
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)
        
        finally:
            client.cleanup()

    def test0114_NRCDtmf_UriGrammar_GlobalCommands_dtmf_Digits(self):
        """
        Test NRC recognition dtmf
        Expect
        1) NRC recognition return successful
        """
        client = gRPCClient()
        test_dtmf = '0'
        test_grammar_type = 'uri_grammar'
        test_grammar_data = 'GlobalCommands_dtmf.grxml'
        test_grammar_uri = client.test_res_url_secure + test_grammar_data
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<SWI_meaning>operator</SWI_meaning><SWI_literal>0</SWI_literal>"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(3)

            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)

            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0115_NRCDtmf_InlineGrammar_Digits_no_input_timeout(self):
        """
        Test NRC recognition dtmf
        Expect
        1)[Test case] NRC recognize return should return code 408, No-Input Timeout
        """
        client = gRPCClient()
        test_dtmf = 'P'
        test_grammar_type = 'inline_grammar'
        test_grammar_data = '<?xml version=\"1.0\"?>\n<grammar  version=\"1.0\" xml:lang=\"en-us\" mode=\"dtmf\" xmlns=\"http://www.w3.org/2001/06/grammar\" tag-format=\"swi-semantics/1.0\" root=\"DTMFDIGITS\" >\n<rule id=\"DTMFDIGITS\" scope=\"public\">\n<one-of>\n<item> 1 <tag> SWI_meaning = \'One\' </tag> </item>\n<item> 2 <tag> SWI_meaning = \'Two\' </tag> </item>\n</one-of>\n</rule>\n</grammar>'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect1 = "code: 408"
        test_expect2 = 'message: \"Audio timeout\"'
        test_expect3 = "details: \"No DTMF received"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(3)

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

    def test0116_NRCDtmf_UriGrammar_GlobalCommands_dtmf_Digits_no_input_timeout(self):
        """
        Test NRC recognition dtmf
        Expect
        1)[Test case] NRC recognize return should return code 408, No-Input Timeout
        """
        client = gRPCClient()

        test_dtmf = 'P'
        test_grammar_type = 'uri_grammar'
        test_grammar_data = 'GlobalCommands_dtmf.grxml'
        test_grammar_uri = client.test_res_url_secure + test_grammar_data
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect1 = "code: 408"
        test_expect2 = 'message: \"Audio timeout\"'
        test_expect3 = "details: \"No DTMF received"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(3)

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

    def test0117_NRCDtmf_UriGrammar_Digits_dtmf_InvalidWeight(self):
        """
        Test NRC recognition dtmf
        Expect
        1)
        a)[Test case] NRC recognize return successful
        b)[Test Case] NRC recognition return successful
        c)[Test Case] NRC recognition should return code: 400, Bad Result, Grammar weight is out of range
        d)[Test Case] NRC recognition should return code: 400, Bad Result, Grammar weight is out of range
        """
        client = gRPCClient()

        test_dtmf1 = '1'
        test_grammar_weight1 = 1
        test_grammar_type = 'uri_grammar'
        test_grammar_data = 'Digits_dtmf.grxml'
        test_grammar_uri = client.test_res_url_secure + test_grammar_data
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                     grammarWeight=test_grammar_weight1)
        test_dtmfrecInit1 = client.dtmfrecognition_init(test_recogParams, test_recogRes1)
        test_expect1 = "<SWI_meaning>1</SWI_meaning><SWI_literal>1</SWI_literal>"

        test_dtmf2 = '7'
        test_grammar_weight2 = 1
        test_expect2 = "<SWI_meaning>9</SWI_meaning><SWI_literal>7</SWI_literal>"
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                     grammarWeight=test_grammar_weight2)
        test_dtmfrecInit2 = client.dtmfrecognition_init(test_recogParams, test_recogRes2)

        test_dtmf3 = '3'
        test_grammar_weight3 = 0
        test_expect3 = "code: 400"
        test_expect4 = 'message: \"Bad Request\"'
        test_expect5 = "details: \"Grammar weight is out of range."
        test_recogRes3 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                     grammarWeight=test_grammar_weight3)
        test_dtmfrecInit3 = client.dtmfrecognition_init(test_recogParams, test_recogRes3)

        test_dtmf4 = '4'
        test_grammar_weight4 = 32768
        test_expect6 = "code: 400"
        test_expect7 = 'message: \"Bad Request\"'
        test_expect8 = "details: \"Grammar weight is out of range."
        test_recogRes4 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                     grammarWeight=test_grammar_weight4)
        test_dtmfrecInit4 = client.dtmfrecognition_init(test_recogParams, test_recogRes4)

        try:
            test_result1 = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf1, dtmfrecInit=test_dtmfrecInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf2, dtmfrecInit=test_dtmfrecInit2)
            time.sleep(1)
            test_result3 = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf3, dtmfrecInit=test_dtmfrecInit3)
            time.sleep(1)
            test_result4 = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf4, dtmfrecInit=test_dtmfrecInit4)
            time.sleep(3)

            msg = "Test result1:\n" + test_result1 + "\n"
            msg += "Test result2:\n" + test_result2 + "\n"
            msg += "Test result3:\n" + test_result3 + "\n"
            msg += "Test result4:\n" + test_result4 + "\n"

            self.debug(msg)

            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect3)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect4)
            self.assertRecognitionResult(inputToCheck=test_result3, expectResult=test_expect5)
            self.assertRecognitionResult(inputToCheck=test_result4, expectResult=test_expect6)
            self.assertRecognitionResult(inputToCheck=test_result4, expectResult=test_expect7)
            self.assertRecognitionResult(inputToCheck=test_result4, expectResult=test_expect8)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0118_NRCDtmf_InlineGrammar_Digits_dtmf_InvalidWeight(self):
        """
        Test NRC recognition dtmf
        Expect
        1)
        a)[Test Case] NRC recognition should return code: 400, Bad Result, Grammar weight is out of range
        b)[Test Case] NRC recognition should return code: 400, Bad Result, Grammar weight is out of range
        """
        client = gRPCClient()

        test_dtmf1 = '1'
        test_grammar_type = 'inline_grammar'
        test_grammar_weight1 = 0
        test_grammar_data = '<?xml version=\"1.0\"?>\n<grammar  version=\"1.0\" xml:lang=\"en-us\" mode=\"dtmf\" xmlns=\"http://www.w3.org/2001/06/grammar\" tag-format=\"swi-semantics/1.0\" root=\"DTMFDIGITS\" >\n<rule id=\"DTMFDIGITS\" scope=\"public\">\n<one-of>\n<item> 1 <tag> SWI_meaning = \'One\' </tag> </item>\n<item> 2 <tag> SWI_meaning = \'Two\' </tag> </item>\n<item> 7 <tag> SWI_meaning = \'Nine\' </tag> </item>\n</one-of>\n</rule>\n</grammar>'
        test_recogParams1 = client.dtmfrecognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data,
                                                     grammarWeight=test_grammar_weight1)
        test_dtmfrecInit1 = client.dtmfrecognition_init(test_recogParams1, test_recogRes1)
        test_expect1 = "code: 400"
        test_expect2 = 'message: \"Bad Request\"'
        test_expect3 = "details: \"Grammar weight is out of range."

        test_dtmf2 = '2'
        test_grammar_weight2 = 32768
        test_recogParams2 = client.dtmfrecognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data,
                                                     grammarWeight=test_grammar_weight2)
        test_dtmfrecInit2 = client.dtmfrecognition_init(test_recogParams2, test_recogRes2)
        test_expect4 = "code: 400"
        test_expect5 = 'message: \"Bad Request\"'
        test_expect6 = "details: \"Grammar weight is out of range."

        try:
            test_result1 = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf1, dtmfrecInit=test_dtmfrecInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf2, dtmfrecInit=test_dtmfrecInit2)
            time.sleep(3)

            msg = "Test result1:\n" + test_result1 + "\n"
            msg += "Test result2:\n" + test_result2 + "\n"
            self.debug(msg)

            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect2)
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect3)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect4)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect5)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect6)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0119_NRCDtmf_UriGrammar_last4PmtAccount(self):
        """
        Test NRC recognition dtmf for external grammar
        Expect
        1) NRC recognition return successful
        """
        client = gRPCClient()
        test_dtmf = '1234'
        test_grammar_type = 'uri_grammar'
        test_grammar_data = 'last4PmtAccount_dtmf.grxml'
        test_grammar_uri = client.test_res_url_secure + test_grammar_data
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<SWI_literal>1 2 3 4</SWI_literal>.+<SWI_meaning>{last4PmtAccount:1234}</SWI_meaning>"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(3)

            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)

            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0120_NRCDtmf_UriGrammar_last4PmtAccount_NO_MATCH(self):
        """
        Test NRC recognition dtmf for external grammar
        Expect
        1) NRC recognition return NO_MATCH
        """
        client = gRPCClient()
        test_dtmf = '123'
        test_grammar_type = 'uri_grammar'
        test_grammar_data = 'last4PmtAccount_dtmf.grxml'
        test_grammar_uri = client.test_res_url_secure + test_grammar_data
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "NO_MATCH"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(3)

            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)

            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0121_NRCDtmf_UriGrammar_last4PmtAccount_no_input_timeout(self):
        """
        Test NRC recognition dtmf for external grammar
        Expect
        1) NRC recognize return should return code 408, No-Input Timeout
        """
        client = gRPCClient()
        test_dtmf = 'P'
        test_grammar_type = 'uri_grammar'
        test_grammar_data = 'last4PmtAccount_dtmf.grxml'
        test_grammar_uri = client.test_res_url_secure + test_grammar_data
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect1 = "code: 408"
        test_expect2 = 'message: \"Audio timeout\"'
        test_expect3 = "details: \"No DTMF received"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(3)

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

    def test0122_NRCDtmf_UriGrammar_pharm0115_PharmacyMenu(self):
        """
        Test NRC recognition dtmf for external grammar
        Expect
        1) NRC recognition return successful
        """
        client = gRPCClient()
        test_dtmf = "1"
        test_grammar_type = 'uri_grammar'
        test_grammar_data = 'pharm0115_PharmacyMenu_DM_dtmf.grxml'
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url_secure + test_grammar_data
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<SWI_meaning>pa_status</SWI_meaning>.+<SWI_literal>1</SWI_literal>"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(3)

            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)

            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0123_NRCDtmf_UriGrammar_pharm0115_PharmacyMenu_NO_MATCH(self):
        """
        Test NRC recognition dtmf for external grammar
        Expect
        1) NRC recognition returns NO MATCH
        """
        client = gRPCClient()
        test_dtmf = "7"
        test_grammar_type = 'uri_grammar'
        test_grammar_data = 'pharm0115_PharmacyMenu_DM_dtmf.grxml'
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url_secure + test_grammar_data
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "NO_MATCH"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(3)

            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)

            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()


    def test0124_NRCGenesys_UriGrammar_Stations333_No_Match(self):
        """
        Test NRC recognition dtmf followed by NRC recognition audio
        Expect
        1)
        a)[Test case] NRC recognize return should return NO_MATCH
        b)[Test Case] NRC recognition return successful
        """
        client = gRPCClient()

        # Recognition request 1: dtmf
        test_dtmf1 = "DATE"
        test_grammar_type1 = 'uri_grammar'
        test_grammar_data1 = 'stations333.grxml'
        test_grammar_uri1 = client.test_res_url_secure + test_grammar_data1
        test_recogParams1 = client.dtmfrecognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_uri1)
        test_dtmfrecInit1 = client.dtmfrecognition_init(test_recogParams1, test_recogRes1)
        test_expect1 = "NO_MATCH"

        # Recognition request 2: audio
        test_audio2 = "date.ulaw"
        # test_audio_format2 = 'pcm'
        test_grammar_type2 = 'uri_grammar'
        test_grammar_data2 = 'stations333.grxml'
        test_grammar_uri2 = client.test_res_url_secure + test_grammar_data2
        test_recogParams2 = client.recognition_parameters()
        test_recogRes2 = client.recognition_resource(grammarType=test_grammar_type2, grammarData=test_grammar_uri2)
        test_recInit2 = client.recognition_init(test_recogParams2, test_recogRes2)
        test_expect2 = "<SWI_meaning>DATEAZ</SWI_meaning><SWI_literal>date</SWI_literal>"

        try:
            test_result1 = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf1, dtmfrecInit=test_dtmfrecInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_recognize_test_func1(audioInput=test_audio2, recInit=test_recInit2)
            time.sleep(1)

            msg = "Test result1:\n" + test_result1 + "\n"
            msg += "Test result2:\n" + test_result2 + "\n"
            self.debug(msg)

            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0125_NRCDtmf_InlineGrammar_Digits(self):
        """
        Test NRC recognition dtmf
        Expect
        1)
        a)[Test case] NRC recognition return successful
        b)[Test Case] NRC recognition return successful
        """
        client = gRPCClient()

        test_dtmf1 = '1'
        test_grammar_type1 = 'inline_grammar'
        test_grammar_data1 = '<?xml version=\"1.0\"?>\n<grammar  version=\"1.0\" xml:lang=\"en-us\" mode=\"dtmf\" xmlns=\"http://www.w3.org/2001/06/grammar\" tag-format=\"swi-semantics/1.0\" root=\"DTMFDIGITS\" >\n<rule id=\"DTMFDIGITS\" scope=\"public\">\n<one-of>\n<item> 1 <tag> SWI_meaning = \'One\' </tag> </item>\n<item> 2 <tag> SWI_meaning = \'Double\' </tag> </item>\n</one-of>\n</rule>\n</grammar>'
        test_recogParams1 = client.dtmfrecognition_parameters()
        test_recogRes1 = client.recognition_resource(grammarType=test_grammar_type1, grammarData=test_grammar_data1)
        test_dtmfrecInit1 = client.dtmfrecognition_init(test_recogParams1, test_recogRes1)
        test_expect1 = "<SWI_meaning>One</SWI_meaning><SWI_literal>1</SWI_literal>"

        test_dtmf2 = '2'
        test_expect2 = "<SWI_meaning>Double</SWI_meaning><SWI_literal>2</SWI_literal>"

        try:
            test_result1 = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf1, dtmfrecInit=test_dtmfrecInit1)
            time.sleep(1)
            test_result2 = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf2, dtmfrecInit=test_dtmfrecInit1)
            time.sleep(3)

            msg = "Test result1:\n" + test_result1 + "\n"
            msg += "Test result2:\n" + test_result2 + "\n"
            self.debug(msg)

            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test0126_NRCDtmf_Send_FinalResult_Immediately_When_DtmfTermChar_Empty(self):

        client = gRPCClient()

        test_dtmf = "12954"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar= ''
        test_dtmfTermTimeout= 20000
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar,dtmfTermTimeout=test_dtmfTermTimeout)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>12954<\/instance.+\/interpretation.+\/result>"
        
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

    def test0127_NRCDtmf_Send_FinalResult_Immediately_When_DtmfTermChar_NotSet(self):

        client = gRPCClient()

        test_dtmf = "12954"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar= None
        test_dtmfTermTimeout= 20000
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar, dtmfTermTimeout=test_dtmfTermTimeout)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>12954<\/instance.+\/interpretation.+\/result>"
        
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

    def test0128_NRCDtmf_Term_CharEmpty_timeout_Zero(self):

        client = gRPCClient()

        test_dtmf = "123"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar = ''
        test_dtmfTermTimeout= 0
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar, dtmfTermTimeout=test_dtmfTermTimeout)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>123<\/instance.+\/interpretation.+\/result>"

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

    def test0129_NRCDtmf_Term_CharNone_timeout_Zero(self):

        client = gRPCClient()

        test_dtmf = "123"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_dtmfTermChar = '#'
        test_dtmfTermTimeout= 0
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar, dtmfTermTimeout=test_dtmfTermTimeout)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>123<\/instance.+\/interpretation.+\/result>"

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

    def test0130_NRCDtmf_length(self):

        client = gRPCClient()

        test_dtmf = "123#456"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits?length=2'
        test_dtmfTermChar = ''
        test_dtmfTermTimeout = 0
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar, dtmfTermTimeout=test_dtmfTermTimeout)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>12<\/instance.+\/interpretation.+\/result>"

        try:

            test_result1 = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result1 + "\n"
            self.debug(msg)

            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)


        finally:
            client.cleanup()

    def test0131_NRCDtmf_length_TermChar(self):

        client = gRPCClient()

        test_dtmf1 = "123456#7"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits?length=4'
        test_dtmfTermTimeout = 0
        test_dtmfTermChar = '#'
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar, dtmfTermTimeout=test_dtmfTermTimeout)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect1 = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1234<\/instance.+\/interpretation.+\/result>"

        test_dtmf2 = "1234#567"
        test_expect2 = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1234<\/instance.+\/interpretation.+\/result>"
        

        try:

            test_result1 = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf1, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            test_result2 = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf2, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            msg = "Test result1:\n" + test_result1 + "\n"
            msg += "Test result2:\n" + test_result2 + "\n"
            self.debug(msg)

            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)


        finally:
            client.cleanup()

    def test0132_NRCDtmf_minMaxLength_TermChar(self):
        client = gRPCClient()

        test_dtmf = "12345#6"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits?minlength=2&maxlength=5'
        test_dtmfTermChar = '#'
        test_dtmfTermTimeout = 0
        test_recogParams = client.dtmfrecognition_parameters(dtmfTermChar=test_dtmfTermChar, dtmfTermTimeout=test_dtmfTermTimeout)
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect1 = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>12345<\/instance.+\/interpretation.+\/result>"

        test_dtmf2 = "1234#567"
        test_expect2 = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1234<\/instance.+\/interpretation.+\/result>"

        try:

            test_result1 = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            test_result2 = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf2, dtmfrecInit=test_dtmfrecInit)
            time.sleep(1)
            msg = "Test result:\n" + test_result1 + "\n"
            msg += "Test result2:\n" + test_result2 + "\n"
            self.debug(msg)

            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result1, expectResult=test_expect1)
            self.assertRecognitionResult(inputToCheck=test_result2, expectResult=test_expect2)


        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)


        finally:
            client.cleanup()

    def test0133_NRCDtmf_uriGrammar_ssn(self):
        """
        Test NRC recognition dtmf for external grammar
        Expect
        1) NRC recognition return successful
        """
        client = gRPCClient()
        test_dtmf = "586209999"
        test_grammar_type = 'uri_grammar'
        test_grammar_data = 'ssn0100_CollectTIN_QA_dtmf.grxml?version=1.0_1695137215822'
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url_secure + test_grammar_data
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri,
                                                    mediaType=test_media_type)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<SWI_meaning>586209999</SWI_meaning>.+<SWI_literal>5 8 6 2 0 9 9 9 9</SWI_literal>"

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            time.sleep(3)

            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)

            print(msg)  # for debug

            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()