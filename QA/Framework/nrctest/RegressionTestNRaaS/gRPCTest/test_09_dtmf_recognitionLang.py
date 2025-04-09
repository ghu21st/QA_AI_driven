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
class NRCTestDtmfRecognitionLang(TestFixture):
    """ NRC DTMF recognition resource language test"""

    def test001_NRCDtmfGeneric(self):
        "Test NRC DTMF recognition with language (en-US)"
        client = gRPCClient()
        
        test_dtmf = "1"
        test_language = 'en-US'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"
        #
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            
            print(msg)  # for debug
            
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test002_NRCDtmf_esUS(self):
        "Test NRC DTMF recognition with language (es-US)"
        client = gRPCClient()
        
        test_dtmf = "1"
        test_language = 'es-US'
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"
        #
        try:
            
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
            
            time.sleep(1)
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            
            print(msg)  # for debug
            
            # validate command response
            self.assertRecognitionResult(inputToCheck=test_result, expectResult=test_expect)
            #
            
        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()

    def test003_NRCDtmf_frCA(self):
        "Test NRC DTMF recognition with language (fr-CA)"
        client = gRPCClient()

        test_language = 'fr-CA'
        test_dtmf = "1"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"
        
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

    def test004_NRCDtmf_itIT(self):
        "Test NRC DTMF recognition with language (it-IT)"
        client = gRPCClient()
        
        test_language = 'it-IT'
        test_dtmf = "1"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"
        
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

    def test005_NRCDtmf_enGB(self):
        "Test NRC DTMF recognition with language (en-GB)"
        client = gRPCClient()
        
        test_language = 'en-GB'
        test_dtmf = "1"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"
        
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

    def test006_NRCDtmf_frFR(self):
        "Test NRC DTMF recognition with language (fr-FR)"
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_language = 'fr-FR'
        test_dtmf = "1"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"

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

    def test007_NRCDtmf_deDE(self):
        "Test NRC DTMF recognition with language (de-DE)"
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_language = 'de-DE'
        test_dtmf = "345"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>345<\/instance.+\/interpretation.+\/result>"

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

    def test008_NRCDtmf_esES(self):
        "Test NRC DTMF recognition with language (es-ES)"
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_language = 'es-ES'
        test_dtmf = "345"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>345<\/instance.+\/interpretation.+\/result>"

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

    def test009_NRCDtmf_nlNL(self):
        "Test NRC DTMF recognition with language (nl-NL)"
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_language = 'nl-NL'
        test_dtmf = "345"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>345<\/instance.+\/interpretation.+\/result>"

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

    def test010_NRCDtmf_fiFI(self):
        "Test NRC DTMF recognition with language (fi-FI)"
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_language = 'fi-FI'
        test_dtmf = "3478"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>3478<\/instance.+\/interpretation.+\/result>"

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

    def test011_NRCDtmf_svSE(self):
        "Test NRC DTMF recognition with language (sv-SE)"
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_language = 'sv-SE'
        test_dtmf = "3478"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>3478<\/instance.+\/interpretation.+\/result>"

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

    def test012_NRCDtmf_nbNO(self):
        "Test NRC DTMF recognition with language (nb-NO)"
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_language = 'no-NO'
        test_dtmf = "3478"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>3478<\/instance.+\/interpretation.+\/result>"

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

    def test013_NRCDtmf_csCZ(self):
        "Test NRC DTMF recognition with language (cs-CZ)"
        client = gRPCClient()
        test_language = 'cs-CZ'
        test_dtmf = "57"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>57<\/instance.+\/interpretation.+\/result>"
    
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

    def test014_NRCDtmf_daDK(self):
        "Test NRC DTMF recognition with language (da-DK)"
        client = gRPCClient()
        
        test_language = 'da-DK'
        test_dtmf = "57"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>57<\/instance.+\/interpretation.+\/result>"

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

    def test015_NRCDtmf_elGR(self):
        "Test NRC DTMF recognition with language (el-GR)"
        client = gRPCClient()
        
        test_language = 'el-GR'
        test_dtmf = "57"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>57<\/instance.+\/interpretation.+\/result>"

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

    def test016_NRCDtmf_hiIN(self):
        "Test NRC DTMF recognition with language (hi-IN)"
        client = gRPCClient()
        
        test_language = 'hi-IN'
        test_dtmf = "57"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>57<\/instance.+\/interpretation.+\/result>"

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

    def test017_NRCDtmf_idID(self):
        "Test NRC DTMF recognition with language (id-ID)"
        client = gRPCClient()
        
        test_language = 'id-ID'
        test_dtmf = "57"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>57<\/instance.+\/interpretation.+\/result>"

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

    def test018_NRCDtmf_jaJP(self):
        "Test NRC DTMF recognition with language (ja-JP)"
        client = gRPCClient()
        
        test_language = 'ja-JP'
        test_dtmf = "57"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>57<\/instance.+\/interpretation.+\/result>"

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

    def test019_NRCDtmf_koKR(self):
        "Test NRC DTMF recognition with language (ko-KR)"
        client = gRPCClient()
        
        test_language = 'ko-KR'
        test_dtmf = "57"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>57<\/instance.+\/interpretation.+\/result>"

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

    def test020_NRCDtmf_plPL(self):
        "Test NRC DTMF recognition with language (pl-PL)"
        client = gRPCClient()
        
        test_language = 'pl-PL'
        test_dtmf = "57"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>57<\/instance.+\/interpretation.+\/result>"

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

    def test021_NRCDtmf_ptBR(self):
        "Test NRC DTMF recognition with language (pt-BR)"
        client = gRPCClient()
        
        test_language = 'pt-BR'
        test_dtmf = "83"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>83<\/instance.+\/interpretation.+\/result>"

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

    def test022_NRCDtmf_ruRU(self):
        "Test NRC DTMF recognition with language (ru-RU)"
        client = gRPCClient()
        
        test_language = 'ru-RU'
        test_dtmf = "83"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>83<\/instance.+\/interpretation.+\/result>"

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

    def test023_NRCDtmf_thTH(self):
        "Test NRC DTMF recognition with language (th-TH)"
        client = gRPCClient()
        
        test_language = 'th-TH'
        test_dtmf = "83"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>83<\/instance.+\/interpretation.+\/result>"

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

    def test024_NRCDtmf_trTR(self):
        "Test NRC DTMF recognition with language (tr-TR)"
        client = gRPCClient()
        
        test_language = 'tr-TR'
        test_dtmf = "83"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>83<\/instance.+\/interpretation.+\/result>"

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

    def test025_NRCDtmf_zhCN(self):
        "Test NRC DTMF recognition with language (zh-CN)"
        client = gRPCClient()
        
        test_language = 'zh-CN'
        test_dtmf = "83"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>83<\/instance.+\/interpretation.+\/result>"

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

    def test026_NRCDtmf_zhHK(self):
        "Test NRC DTMF recognition with language (zh-HK)"
        client = gRPCClient()
        
        test_language = 'zh-HK'
        test_dtmf = "83"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>83<\/instance.+\/interpretation.+\/result>"

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

    def test027_NRCDtmf_zhTW(self):
        "Test NRC DTMF recognition with language (zh-TW)"
        client = gRPCClient()
        
        test_language = 'zh-TW'
        test_dtmf = "83"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>83<\/instance.+\/interpretation.+\/result>"

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

    def test028_NRCDtmf_enAU(self):
        "Test NRC DTMF recognition with language (en-AU)"
        client = gRPCClient()
        
        test_language = 'en-AU'
        test_dtmf = "157"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>157<\/instance.+\/interpretation.+\/result>"

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

    def test029_NRCDtmf_caES(self):
        "Test NRC DTMF recognition with language (ca-ES)"
        client = gRPCClient()
        
        test_language = 'ca-ES'
        test_dtmf = "157"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>157<\/instance.+\/interpretation.+\/result>"

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

    def test030_NRCDtmf_esMX(self):
        "Test NRC DTMF recognition with language (es-MX)"
        client = gRPCClient()
        
        test_language = 'es-MX'
        test_dtmf = "157"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>157<\/instance.+\/interpretation.+\/result>"

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

    def test031_NRCDtmf_ptPT(self):
        "Test NRC DTMF recognition with language (pt-PT)"
        client = gRPCClient()
        
        test_language = 'pt-PT'
        test_dtmf = "157"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>157<\/instance.+\/interpretation.+\/result>"

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

    def test032_NRCDtmf_hrHR(self):
        "Test NRC DTMF recognition with language (hr-HR)"
        client = gRPCClient()
        
        test_language = 'hr-HR'
        test_dtmf = "157"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>157<\/instance.+\/interpretation.+\/result>"

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

    def test033_NRCDtmf_huHU(self):
        "Test NRC DTMF recognition with language (hu-HU)"
        client = gRPCClient()
        
        test_language = 'hu-HU'
        test_dtmf = "157"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>157<\/instance.+\/interpretation.+\/result>"

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

    def test034_NRCDtmf_skSK(self):
        "Test NRC DTMF recognition with language (sk-SK)"
        client = gRPCClient()
        
        test_language = 'sk-SK'
        test_dtmf = "248"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>248<\/instance.+\/interpretation.+\/result>"

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

    def test035_NRCDtmf_roRO(self):
        "Test NRC DTMF recognition with language (ro-RO)"
        client = gRPCClient()
        
        test_language = 'ro-RO'
        test_dtmf = "248"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>248<\/instance.+\/interpretation.+\/result>"

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

    def test036_NRCDtmf_msMY(self):
        "Test NRC DTMF recognition with language (ms-MY)"
        client = gRPCClient()
        
        test_language = 'ms-MY'
        test_dtmf = "248"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>248<\/instance.+\/interpretation.+\/result>"

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

    def test037_NRCDtmf_heIL(self):
        "Test NRC DTMF recognition with language (he-IL)"
        client = gRPCClient()
        
        test_language = 'he-IL'
        test_dtmf = "248"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>248<\/instance.+\/interpretation.+\/result>"

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

    def test038_NRCDtmf_viVN(self):
        "Test NRC DTMF recognition with language (vi-VN)"
        client = gRPCClient()
        
        test_language = 'vi-VN'
        test_dtmf = "248"
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data, languageIn=test_language)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes)
        #test_result = ""
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>248<\/instance.+\/interpretation.+\/result>"

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








    

    