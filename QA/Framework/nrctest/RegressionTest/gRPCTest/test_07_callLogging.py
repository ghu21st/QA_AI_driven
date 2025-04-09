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
from TestContext import *

# ------- NRC automation test class -----------
class NRCTestCallLogging(TestFixture):
    """ NRC Call Logging test"""

    def test001_NRCCallLoggingGeneric1(self):
        """
        Test call logs for digits audio recognition using builtin digits grammar
        Expect
        1) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Prompt text and recognition results appear in the call logs
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

        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Endpointer", "Grammar"])
        test_record_1.add_token_to_checklist(evnt="SWIgrld", token="URI", value="builtin:grammar/digits")
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=test_expect)
        test_record_1.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value="grammar=.+builtin:grammar\/digits")
        #
        try:
            test_result = client.qa_nr_recognize_test_func1(audioInput=test_audio, recInit=test_recInit)
            time.sleep(1)
            kafka.validate_callLogs(test_record_1)
            #
            msg = "Test result:\n" + test_result + "\n"
            self.debug(msg)
            print(msg)

        except (AssertionError, TimeoutException, Exception) as e:
            self.fail(e)

        finally:
            client.cleanup()
            kafka.cleanup()


    def test002_UserIdGeneric_Audio(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check generic characters user_id in call logs with expected generated SHA256 value
        """        
        client = gRPCClient()
        kafka = KafkaModule(self)
        context = TestContext()
        
        test_audio = 'yes.ulaw'
        test_grammar = "uri_grammar_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        appId = context.config['NRCTestMetadata']["x-nuance-client-id"].split(":")[1]
        
        test_user_id = "Capitaine Haddock"
        hashedId = self.generateSHA256('{}:{}'.format(appId,test_user_id))
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes, user_id=test_user_id)
        
        # Expected fail - defect is tracked here (https://ent-jira.nuance.com/browse/ENRX-3270)
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, user_id=hashedId)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)

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


    def test003_UserIdGeneric_Dtmf(self):
        """
        Test NRC recognition URI grammar with dtmf digits
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check generic characters user_id in call logs with expected generated SHA256 value
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        context = TestContext()

        test_dtmf = "1"
       
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_user_id = "Capitaine Haddock"
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes, user_id=test_user_id)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"
        appId = context.config['NRCTestMetadata']["x-nuance-client-id"].split(":")[1]
        hashedId = self.generateSHA256('{}:{}'.format(appId,test_user_id))
        
        # Expected fail - defect is tracked here (https://ent-jira.nuance.com/browse/ENRX-3270)
        test_record_1 = kafka.create_messages_record(recogInit=test_dtmfrecInit, expected_result=test_expect, user_id=hashedId)
        test_record_1.set_checklist_types("Grammar")
        test_record_1.add_expression_to_checklist(test_expect)

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
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


    def test004_UserIdDigits_Audio(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check digits user_id in call logs with expected generated SHA256 value
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        context = TestContext()
        
        test_audio = 'yes.ulaw'
        test_grammar = "uri_grammar_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"
        appId = context.config['NRCTestMetadata']["x-nuance-client-id"].split(":")[1]

        test_user_id = "27830029someCHARacters12943045"
        hashedId = self.generateSHA256('{}:{}'.format(appId,test_user_id))
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes, user_id=test_user_id)
        
        # Expected fail - defect is tracked here (https://ent-jira.nuance.com/browse/ENRX-3270)
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, user_id=hashedId)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)

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


    def test005_UserIdDigits_Dtmf(self):
        """
        Test NRC recognition URI grammar with dtmf digits
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check digits user_id in call logs with expected generated SHA256 value
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        context = TestContext()

        test_dtmf = "1"
       
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_user_id = "27830029someCHARacters12943045"
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes, user_id=test_user_id)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"
        appId = context.config['NRCTestMetadata']["x-nuance-client-id"].split(":")[1]
        hashedId = self.generateSHA256('{}:{}'.format(appId,test_user_id))
        
        # Expected fail - defect is tracked here (https://ent-jira.nuance.com/browse/ENRX-3270)
        test_record_1 = kafka.create_messages_record(recogInit=test_dtmfrecInit, expected_result=test_expect, user_id=hashedId)
        test_record_1.set_checklist_types("Grammar")
        test_record_1.add_expression_to_checklist(test_expect)

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
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


    def test006_UserIdSpecialSymbols_Audio(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check special symbols user_id in call logs with expected generated SHA256 value
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        context = TestContext()
        
        test_audio = 'yes.ulaw'
        test_grammar = "uri_grammar_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_user_id = "q̴̪̺͖͔̻̈́d̴̢̗͖̺̼̽q̷̥͌̓ẃ̴̡̳̪ͅḏ̵̯̥̤̽͐̈ 雨中 (8vpE[M pnaNW*XS10MN R[C1A)H*P#@"
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes, user_id=test_user_id)
        appId = context.config['NRCTestMetadata']["x-nuance-client-id"].split(":")[1]
        hashedId = self.generateSHA256('{}:{}'.format(appId,test_user_id))
        
        # Expected fail - defect is tracked here (https://ent-jira.nuance.com/browse/ENRX-3270)
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, user_id=hashedId)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)

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


    def test007_UserIdSpecialSymbols_Dtmf(self):
        """
        Test NRC recognition URI grammar with dtmf digits
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check special symbols user_id in call logs with expected generated SHA256 value
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        context = TestContext()

        test_dtmf = "1"
       
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_user_id = "(8vpE[M  pnaNW*XS10MN R[C1A)H*P#@"
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes, user_id=test_user_id)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"
        appId = context.config['NRCTestMetadata']["x-nuance-client-id"].split(":")[1]
        hashedId = self.generateSHA256('{}:{}'.format(appId,test_user_id))
        
        # Expected fail - defect is tracked here (https://ent-jira.nuance.com/browse/ENRX-3270)
        test_record_1 = kafka.create_messages_record(recogInit=test_dtmfrecInit, expected_result=test_expect, user_id=hashedId)
        test_record_1.set_checklist_types("Grammar")
        test_record_1.add_expression_to_checklist(test_expect)

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
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


    def test008_UserIdEscapeCharacters_Audio(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check escape characters user_id in call logs with expected generated SHA256 value
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        context = TestContext()
        
        test_audio = 'yes.ulaw'
        test_grammar = "uri_grammar_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_user_id = "\n\t\a"
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes, user_id=test_user_id)
        appId = context.config['NRCTestMetadata']["x-nuance-client-id"].split(":")[1]
        hashedId = self.generateSHA256('{}:{}'.format(appId,test_user_id))
        
        # Expected fail - defect is tracked here (https://ent-jira.nuance.com/browse/ENRX-3270)
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, user_id=hashedId)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)

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


    def test009_UserIdEscapeCharacters_Dtmf(self):
        """
        Test NRC recognition URI grammar with dtmf digits
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check escape characters user_id in call logs with expected generated SHA256 value
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        context = TestContext()

        test_dtmf = "1"
       
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_user_id = "\n\t\a"
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes, user_id=test_user_id)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"
        appId = context.config['NRCTestMetadata']["x-nuance-client-id"].split(":")[1]
        hashedId = self.generateSHA256('{}:{}'.format(appId,test_user_id))
        
        # Expected fail - defect is tracked here (https://ent-jira.nuance.com/browse/ENRX-3270)
        test_record_1 = kafka.create_messages_record(recogInit=test_dtmfrecInit, expected_result=test_expect, user_id=hashedId)
        test_record_1.set_checklist_types("Grammar")
        test_record_1.add_expression_to_checklist(test_expect)

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
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


    def test010_UserIdLong_Audio(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check long (300 char) user_id in call logs with expected generated SHA256 value
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        context = TestContext()
        
        test_audio = 'yes.ulaw'
        test_grammar = "uri_grammar_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_user_id = "$Z,bTx~,T@EW8k8G~pZ$Z3nm~VC+jgQZ+R\[G$Jx[,+bLj\R9Ucg_qk^!M%!LchpK~d(5D>Uh8MK9w(r7*y2:HLS}bdajhKaca5G>{FMB&cNQtbhG3[%=Az;BC;BCk${47{k2]sqp7K@L$(Pt!v#=SYa&\pVVb{a}}2[gk`v(Fakb)RuB?nkDd(vsm7th7rfr{ns^z[rz]s[ACh]gv_Kz#VG-jR,&X;,V?`Fd+Mu5Vk=-j-=E9wUC8(}'r*E:t{_TF)+J=5N887}6;s4`,L)Yy#SK4sTRm^$,%eYz9<?yS+*B_Ex87?f=RPnb76J9ZeMnj<L9$r.n^ZP-,3MKHJp..A(D?h^EnyHnh*,+:T/awQ$%*f_kk*/KKkqS"
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes, user_id=test_user_id)
        appId = context.config['NRCTestMetadata']["x-nuance-client-id"].split(":")[1]
        hashedId = self.generateSHA256('{}:{}'.format(appId,test_user_id))
        
        # Expected fail - defect is tracked here (https://ent-jira.nuance.com/browse/ENRX-3270)
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, user_id=hashedId)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)

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


    def test011_UserIdLong_Dtmf(self):
        """
        Test NRC recognition URI grammar with dtmf digits
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check digits user_id in call logs with expected generated SHA256 value
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        context = TestContext()

        test_dtmf = "1"
       
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_user_id = "$Z,bTx~,T@EW8k8G~pZ$Z3nm~VC+jgQZ+R\[G$Jx[,+bLj\R9Ucg_qk^!M%!LchpK~d(5D>Uh8MK9w(r7*y2:HLS}bdajhKaca5G>{FMB&cNQtbhG3[%=Az;BC;BCk${47{k2]sqp7K@L$(Pt!v#=SYa&\pVVb{a}}2[gk`v(Fakb)RuB?nkDd(vsm7th7rfr{ns^z[rz]s[ACh]gv_Kz#VG-jR,&X;,V?`Fd+Mu5Vk=-j-=E9wUC8(}'r*E:t{_TF)+J=5N887}6;s4`,L)Yy#SK4sTRm^$,%eYz9<?yS+*B_Ex87?f=RPnb76J9ZeMnj<L9$r.n^ZP-,3MKHJp..A(D?h^EnyHnh*,+:T/awQ$%*f_kk*/KKkqS"
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes, user_id=test_user_id)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"
        appId = context.config['NRCTestMetadata']["x-nuance-client-id"].split(":")[1]
        hashedId = self.generateSHA256('{}:{}'.format(appId,test_user_id))
        
        # Expected fail - defect is tracked here (https://ent-jira.nuance.com/browse/ENRX-3270)
        test_record_1 = kafka.create_messages_record(recogInit=test_dtmfrecInit, expected_result=test_expect, user_id=hashedId)
        test_record_1.set_checklist_types("Grammar")
        test_record_1.add_expression_to_checklist(test_expect)

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
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


    def test012_UserIdInvalidEmtpyString_Audio(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check empty string user_id does not create UserId event in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = 'yes.ulaw'
        test_grammar = "uri_grammar_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_user_id = ""
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes, user_id=test_user_id)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, user_id=None)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)

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


    def test013_UserIdInvalidEmtpyString_Dtmf(self):
        """
        Test NRC recognition URI grammar with dtmf digits
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check empty string user_id in call logs with expected generated SHA256 value
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_dtmf = "1"
       
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_user_id = ""
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes, user_id=test_user_id)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_dtmfrecInit, expected_result=test_expect, user_id=None)
        test_record_1.set_checklist_types("Grammar")
        test_record_1.add_expression_to_checklist(test_expect)

        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
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


    def test014_UserIdInvalidNone_Audio(self):
        """
        Test NRC recognition URI grammar with audio 'yes.ulaw'
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check None user_id does not create UserId event in the call logs
        """
        client = gRPCClient()
        kafka = KafkaModule(self)
        
        test_audio = 'yes.ulaw'
        test_grammar = "uri_grammar_yes.grxml"
        test_grammar_type = "uri_grammar"
        test_media_type = 'srgsxml'
        test_grammar_uri = client.test_res_url + test_grammar
        test_expect = "<?xml.+><result><interpretation grammar=.+confidence=.+<instance><SWI_literal>yes</SWI_literal>.+<SWI_meaning.+yes.+SWI_meaning></instance></interpretation></result>"

        test_user_id = None
        test_recogParams = client.recognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_uri, mediaType=test_media_type)
        test_recInit = client.recognition_init(test_recogParams, test_recogRes, user_id=test_user_id)
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_recInit, expected_result=test_expect, user_id=None)
        test_record_1.set_checklist_types(["Basic", "Recognition", "Grammar", "Endpointer"])
        test_record_1.add_expression_to_checklist(test_expect)

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


    def test015_UserIdInvalidNone_Dtmf(self):
        """
        Test NRC recognition URI grammar with dtmf digits
        Expect:
        1) [Test case] NRC recognize return successful
        2) [Automation call log validation] verify NRC call log from this case via QA NRC call logging support (see doc & demo: https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599);
            a) Check None user_id in call logs with expected generated SHA256 value
        """
        client = gRPCClient()
        kafka = KafkaModule(self)

        test_dtmf = "1"
       
        test_grammar_type = 'builtin:dtmf'
        test_grammar_data = 'digits'
        test_user_id = None
        test_recogParams = client.dtmfrecognition_parameters()
        test_recogRes = client.recognition_resource(grammarType=test_grammar_type, grammarData=test_grammar_data)
        test_dtmfrecInit = client.dtmfrecognition_init(test_recogParams, test_recogRes, user_id=test_user_id)
        test_expect = "<result><interpretation grammar=.+builtin:dtmf\/digits.+<instance>1<\/instance.+\/interpretation.+\/result>"
        #
        test_record_1 = kafka.create_messages_record(recogInit=test_dtmfrecInit, expected_result=test_expect, user_id=None)
        test_record_1.set_checklist_types("Grammar")
        test_record_1.add_expression_to_checklist(test_expect)
        
        try:
            test_result = client.qa_nr_dtmfrecognize_test_func1(dtmfInput=test_dtmf, dtmfrecInit=test_dtmfrecInit)
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