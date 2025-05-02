import re
import json
import jsonschema

class MessagesRecord:

    def __init__(self, recogInit, expected_result, result_status, status_code, status_message, secure_clog, user_id): #, dtmf=False):
        self.recogInit = recogInit
        self.expected_result = expected_result
        self.result_status = result_status
        self.status_code = status_code
        self.status_message = status_message
        self.secure_clog = secure_clog
        self.user_id = user_id
        # Request CHAN id and number in sequence of calls.
        self.msg_nbre = 0
        self.req_nbre = 0
        self.app_id = None
        self.request_id = None
        self.ids = []
        # Initialize checklist as empty list.
        self.checklist = self.Checklist()
        # Initialize private previous time value variable, used to validate call logs timestamps sequence.
        self.__prev_time_val = 0

    # ------------------------ Requests types Validation methods ------------------------ #

    def perform_top_values_checks(self, message_value):
        if None == self.app_id: self.app_id = message_value["appid"]
        # Define schema template we want the actual call logs to look like
        TOP_VALUES_SCHEMA = {
            "type" : "object", "additionalProperties": False, "minProperties": 9,
            "properties" : {
                "specversion":     {"const": "1.0"},
                "service":         {"const": "NRaaS"},
                "source":          {"enum": ["nuance.nrc.v1.NRC/Recognize", "nuance.nrc.v1.NRC/DTMFRecognize"]},
                "type":            {"enum": ["Recognize", "DTMFRecognize"]},
                "id":              {"not": {"enum": self.ids}}, # Check unique id
                "timestamp":       {"pattern": ".+"}, #TODO: set regex needed for timestamp
                "appid":           {"const": self.app_id}, # Check same appid
                "datacontenttype": {"const": "application/json"},
                "data":            {"type": "object"}
            }
        }
        error_string = self.validateJson(jsonData=message_value, schema=TOP_VALUES_SCHEMA)
        # Add id to the list of ids
        self.ids.append(message_value["id"])
        return error_string

    def perform_recognitionInit_checks(self, data_value):
        if None == self.request_id: self.request_id = data_value["requestid"]
        # Possible enhancement: Add Recognition_init details in the schema
        expected_resources = {"type": "array"}
        if self.secure_clog: expected_resources = {"string": "_SUPPRESSED"}
        expected_user_id = {"type": "string"}
        if self.user_id != None: expected_user_id = {"const": self.user_id}
        dataContentType = "application/x-nuance-nrc-recognitioninit.v1+json"
        if data_value["dataContentType"] == "application/x-nuance-nrc-dtmfrecognitioninit.v1+json":
            dataContentType = "application/x-nuance-nrc-dtmfrecognitioninit.v1+json"

        DATA_VALUES_SCHEMA = {
            "type" : "object", #"additionalProperties": False, "minProperties": 6,
            "properties" : {
                "dataContentType": {"const": dataContentType},
                "nrcSessionid":    {"type": "string"},
                "traceid":         {"type": "string"}, # could be anything if jaeger used (TODO)
                "requestid":       {"const": self.request_id}, # should always be same
                "clientRequestid": {"type": "string"},
                "locale":          {"const": "en-US"},
                "request": {
                    "type": "object", "additionalProperties": False, "minProperties": 1,
                    "properties": {
                        "recognitionInit": {
                            "type": "object", "additionalProperties": False, "minProperties": 2,
                            "properties": {
                                "parameters": {"type": "object"},
                                "resources":  expected_resources,
                                "userId":     expected_user_id
                            }
                        }
                    }
                }
            }
        }
        error_string = self.validateJson(jsonData=data_value, schema=DATA_VALUES_SCHEMA)
        return error_string
    

    def perform_status_checks(self, data_value):
        if None == self.request_id: self.request_id = data_value["requestid"]
        DATA_VALUES_SCHEMA = {
            "type" : "object", "additionalProperties": False, "minProperties": 6,
            "properties" : {
                "dataContentType": {"const": "application/x-nuance-nrc-status.v1+json"},
                "nrcSessionid":    {"type": "string"},
                "traceid":         {"type": "string"}, # could be anything if jaeger used (TODO)
                "requestid":       {"const": self.request_id}, # should always be same
                "clientRequestid": {"type": "string"},
                "userid":          {"type": "string"},
                "locale":          {"const": "en-US"},
                "processingTime":  {"type": "object"},
                "response": {
                    "type": "object", "additionalProperties": False, "minProperties": 1,
                    "properties": {
                        "status": {
                            "type": "object", "additionalProperties": False, "minProperties": 2,
                            "properties": {
                                "code":     {"enum": [self.status_code, 200]},
                                "message":  {"enum": [self.status_message, "OK"]},
                                "details":  {"type:": "string"}
                            }
                        }
                    }
                }
            }
        }
        error_string = self.validateJson(jsonData=data_value, schema=DATA_VALUES_SCHEMA)
        return error_string

    def perform_startOfSpeech_checks(self, data_value):
        if None == self.request_id: self.request_id = data_value["requestid"]
        DATA_VALUES_SCHEMA = {
            "type" : "object", "additionalProperties": False, "minProperties": 6,
            "properties" : {
                "dataContentType": {"const": "application/x-nuance-nrc-startofspeech.v1+json"},
                "nrcSessionid":          {"type": "string"},
                "traceid":         {"type": "string"}, # could be anything if jaeger used (TODO)
                "requestid":       {"const": self.request_id}, # should always be same
                "clientRequestid": {"type": "string"},
                "locale":          {"const": "en-US"},
                "userid":          {"type": "string"},
                "processingTime":  {"type": "object"},
                "response": {
                    "type": "object", "additionalProperties": False, "minProperties": 1,
                    "properties": {
                        "startOfSpeech": {
                            "type": "object", #"additionalProperties": False, "minProperties": 1,
                            "properties": {
                                "firstAudioToStartOfSpeechMs": {"type": "number"},
                            }
                        }
                    }
                }
            }
        }
        error_string = self.validateJson(jsonData=data_value, schema=DATA_VALUES_SCHEMA)
        return error_string

    def perform_endOfSpeech_checks(self, data_value):
        if None == self.request_id: self.request_id = data_value["requestid"]
        DATA_VALUES_SCHEMA = {
            "type" : "object", "additionalProperties": False, "minProperties": 6,
            "properties" : {
                "dataContentType": {"const": "application/x-nuance-nrc-endofspeech.v1+json"},
                "nrcSessionid":          {"type": "string"},
                "traceid":         {"type": "string"}, # could be anything if jaeger used (TODO)
                "requestid":       {"const": self.request_id}, # should always be same
                "clientRequestid": {"type": "string"},
                "locale":          {"const": "en-US"},
                "processingTime":  {"type": "object"},
                "userid":          {"type": "string"},
                "response": {
                    "type": "object", "additionalProperties": False, "minProperties": 1,
                    "properties": {
                        "endOfSpeech": {
                            "type": "object", "additionalProperties": False, "minProperties": 1,
                            "properties": {
                                "firstAudioToEndOfSpeechMs": {"type": "number"},
                            }
                        }
                    }
                }
            }
        }
        error_string = self.validateJson(jsonData=data_value, schema=DATA_VALUES_SCHEMA)
        return error_string

    def perform_result_checks(self, data_value):
        if None == self.request_id: self.request_id = data_value["requestid"]
        expected_result = self.expected_result
        if self.secure_clog: expected_result = "_SUPPRESSED"
        
        DATA_VALUES_SCHEMA = {
            "type" : "object", "additionalProperties": False, "minProperties": 6,
            "properties" : {
                "dataContentType": {"const": "application/x-nuance-nrc-result.v1+json"},
                "nrcSessionid":          {"type": "string"},
                "traceid":         {"type": "string"}, # could be anything if jaeger used (TODO)
                "requestid":       {"const": self.request_id}, # should always be same
                "clientRequestid": {"type": "string"},
                "userid":          {"type": "string"},
                "locale":          {"const": "en-US"},
                "processingTime": {
                    "type": "object", "additionalProperties": False, "minProperties": 2,
                    "properties": {
                        "startTime":  {"pattern": ".+"}, #TODO: set regex needed for time
                        "durationMs": {"type": "number"}
                    }
                },
                "response": {
                    "type": "object", "additionalProperties": False, "minProperties": 1,
                    "properties": {
                        "result": {
                            "type": "object", "additionalProperties": False,
                            "properties": {
                                "formattedText": {"pattern": expected_result},
                                "status":        {"const": self.result_status}
                            }
                        }
                    }
                }
            }
        }
        error_string = self.validateJson(jsonData=data_value, schema=DATA_VALUES_SCHEMA)
        return error_string

    def perform_callsummary_checks(self, data_value, data_pair=""):
        if None == self.request_id: self.request_id = data_value["requestid"]
        DATA_VALUES_SCHEMA = {
            "type" : "object", "additionalProperties": False, "minProperties": 7,
            "properties" : {
                "dataContentType": {"const": "application/x-nuance-nrc-callsummary.v1+json"},
                "nrcSessionid":    {"type": "string"},
                "traceid":         {"type": "string"}, # could be anything if jaeger used (TODO)
                "requestid":       {"const": self.request_id}, # should always be same
                "clientRequestid": {"type": "string"},
                #"userid":          {"type": "string"},
                "locale":          {"const": "en-US"},
                "processingTime": {
                    "type": "object", "additionalProperties": False, "minProperties": 2,
                    "properties": {
                        "startTime":  {"pattern": ".+"}, #TODO: set regex needed for time
                        "durationMs": {"type": "number"}
                    }
                },
                "callsummary": {"type": "object"}
            }
        }
        # print("********* VALIDATE *********")
        error_string = ""
        error_string = self.validateJson(jsonData=data_value, schema=DATA_VALUES_SCHEMA)
        
        # Validate call summary events logs. Most important validation for the call logs
        callsummary_logs = data_value["callsummary"]
        for event_message_key,event_message in callsummary_logs.items():
            if event_message_key == 'absEndTime':
                  isinstance(event_message,int)
            if event_message_key == 'status': 
                  self.checklist.validate_event_status(event_message=event_message)
            if event_message_key == 'audioPacketStats':
                if data_pair == '':
                    self.checklist.validate_event_audioPacketStats(event_message=event_message)
                else:
                    self.checklist.validate_event_audioPacketValue(event_message, data_pair)
            if event_message_key =='nrcalllogs':
                for nrc_log_message in event_message:
                    self.checklist.validate_event(event_message=nrc_log_message)
        # Append errors to error_string
        return error_string
    

    def close(self):
        return self.checklist.close(self.req_nbre)


    @staticmethod
    def validateJson(jsonData, schema):
        """ Helper converts json validation result to Boolean """
        # print("\n\n$$$$$$$$ JSON DATA $$$$$$\n\n",jsonData)
        # print("\n\n$$$$$$$$ SCHEMA $$$$$$\n\n",schema)
        try:
            jsonschema.validate(instance=jsonData, schema=schema)
            return ""
        except jsonschema.exceptions.ValidationError as err:
            return err.message

    @staticmethod
    def validateValue(jsonData, data_pair):
        var, vul = data_pair.split('=')
        try:
            for x,y in jsonData.items():
                if x == var:
                    if int(y) >= int(vul):
                        print ("Verified %s = %d seconds" % (x, int(y)))
                        return ""
                    else:
                        return "%s does not martch expected %s" % (var,str(vul))
        except Exception as err:
            return err.message

    # --------------- functions for message record's checklist --------------- #
        
    def set_checklist_types(self, request_types):
        return self.checklist.set_types(request_types)
    
    def add_event_to_checklist(self, event, value):
        return self.checklist.add_event_to_checklist(event, value)
    
    def add_token_to_checklist(self, evnt, token, value):
        return self.checklist.add_token_to_checklist(evnt, token, value)

    def add_expression_to_checklist(self, expression):
        return self.checklist.add_expression_to_checklist(expression)

    def add_sequence_to_checklist(self, sequence: list):
        return self.checklist.add_sequence_to_checklist(sequence)

    def add_undesired_to_checklist(self, undesired):
        return self.checklist.add_undesired_to_checklist(undesired)
        
    # ---------------------------------------------------------------------------- #

    class Checklist:
        def __init__(self):
             self.chan_id = None
             self.checks = []
        
            # --------------------------- Checklist handling methods --------------------------- #

        def set_types(self, request_types):  
            """
            Sets MessagesRecord request type to update checklist of validations for call logs.
            @input: 1 string or list of request types used to validate call logs.

            REQUEST TYPES: Endpointers, Recognition, Grammar
            POSSIBLE CHECKS: value, sequence, token, expression 
            """
            # Validate input.    
            if type(request_types) == str:
                request_types = [request_types]
            elif type(request_types) != list:
                raise Exception("Expected Request Types List passed as list. Datatype received: " + str(type(request_types)))

            # Based on request type, add checks to checklist.
            for req_type in request_types:
                # Part 4 of [QA] NRC call logging manual tests - Basic format/events/recognitions - 1 https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599
                if req_type == "Basic":
                    self.add_token_to_checklist(evnt="SWIrcnd", token="CONF", value=".+")
                    self.add_token_to_checklist(evnt="SWIrcnd", token="DURS", value=".+")
                    self.add_token_to_checklist(evnt="SWIrcnd", token="EOST", value=".+")
                    self.add_token_to_checklist(evnt="SWIrcnd", token="EORT", value=".+")
                    self.add_token_to_checklist(evnt="SWIrcnd", token="EOSS", value=".+")
                    self.add_token_to_checklist(evnt="SWIrcnd", token="RCPU", value=".+")
                    # self.add_token_to_checklist(evnt="SWIrcnd", token="PLAYABLE", value=".+")
                    self.add_token_to_checklist(evnt="NUANwvfm", token="PLAYABLE", value=".+")
                
                elif req_type == "Endpointer":
                    # Part 5 of [QA] NRC call logging manual tests - Basic format/events/recognitions - 1 https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599
                    self.add_event_to_checklist(event="EVNT", value="SWIfrmt")
                    self.add_event_to_checklist(event="EVNT", value="SWIepst")
                    self.add_event_to_checklist(event="EVNT", value="SWIepms")
                    self.add_event_to_checklist(event="EVNT", value="SWIepss")
                    self.add_event_to_checklist(event="EVNT", value="SWIepse")
                
                elif req_type == "Recognition":
                    # Part 6 of [QA] NRC call logging manual tests - Basic format/events/recognitions - 1 https://confluence.labs.nuance.com/pages/viewpage.action?pageId=183936599
                    evnt0 = self.add_event_to_checklist(event="EVNT", value="SWIrcst")
                    evnt1 = self.add_event_to_checklist(event="EVNT", value="NUANwvfm")
                    evnt2 = self.add_event_to_checklist(event="EVNT", value="SWIrcnd")
                    evnt3 = self.add_event_to_checklist(event="EVNT", value="SWIrslt")
                    self.add_sequence_to_checklist([evnt0, evnt1, evnt2, evnt3])
                    #
                    evnt4 = self.add_event_to_checklist(event="EVNT", value="SWIliss")
                    evnt5 = self.add_event_to_checklist(event="EVNT", value="SWIlise")
                    self.add_sequence_to_checklist([evnt4, evnt5])
                    #
                    evnt6 = self.add_event_to_checklist(event="EVNT", value="SWIfrmt")
                    evnt7 = self.add_event_to_checklist(event="EVNT", value="SWIclst")
                    evnt8 = self.add_event_to_checklist(event="EVNT", value="NUANtnat")
                    evnt9 = self.add_event_to_checklist(event="EVNT", value="SWIclnd")
                    self.add_sequence_to_checklist([evnt6, evnt7, evnt8, evnt9])
                
                elif req_type == "Grammar":
                    # [QA] NRC call logging manual tests - Grammar-2 https://confluence.labs.nuance.com/display/IM/%5BQA%5D+NRC+call+logging+manual+tests+-+Grammar-2
                    self.add_token_to_checklist(evnt="SWIgrld", token="API", value="SWIrecGrammarLoad|SWIrecGrammarActivate|SWIrecGrammarCompile")
                    self.add_token_to_checklist(evnt="SWIgrld", token="COMPILES", value=".+")
                    self.add_token_to_checklist(evnt="SWIgrld", token="DISKHITS", value=".+")
                    self.add_token_to_checklist(evnt="SWIgrld", token="DISKMISS", value=".+")
                    self.add_token_to_checklist(evnt="SWIgrld", token="FETCHES", value=".+")
                    self.add_token_to_checklist(evnt="SWIgrld", token="GCCPU", value=".+")
                    self.add_token_to_checklist(evnt="SWIgrld", token="GCTIME", value=".+")
                    self.add_token_to_checklist(evnt="SWIgrld", token="IFCPU", value=".+")
                    self.add_token_to_checklist(evnt="SWIgrld", token="IFTIME", value=".+")
                    self.add_token_to_checklist(evnt="SWIgrld", token="IFBYTES", value=".+")
                    self.add_token_to_checklist(evnt="SWIgrld", token="LDCPU", value=".+")
                    self.add_token_to_checklist(evnt="SWIgrld", token="LDTIME", value=".+")
                    self.add_token_to_checklist(evnt="SWIgrld", token="MEMMISS", value=".+")
                    self.add_token_to_checklist(evnt="SWIgrld", token="MEMHITS", value=".+")
                    self.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value=".+")
                    self.add_token_to_checklist(evnt="SWIgrld", token="RC", value=".+")
                    self.add_token_to_checklist(evnt="SWIgrld", token="TYPE", value=".+")
                
                elif req_type == "DTMF":
                    # [QA] NRC call logging manual tests - DTMF https://confluence.labs.nuance.com/display/IM/%5BQA%5D+NRC+call+logging+manual+tests+-+DTMF-8
                    self.add_token_to_checklist(evnt="SWIgrld", token="URI", value=".+")
                    self.add_token_to_checklist(evnt="SWIgrld", token="PROPS", value=".+")
                    self.add_token_to_checklist(evnt="SWIrslt", token="CNTNT", value=".+")

                else:
                    raise Exception("Invalid type \"" + req_type + "\" was passed for request. Verify list of acceptable request types.")

        def add_event_to_checklist(self, event, value):
            check = self.ChecklistElement(type="value", args=[event,str(value)])
            self.checks.append(check)
            return check
            
        def add_token_to_checklist(self, evnt, token, value):
            check = self.ChecklistElement(type="token", args=[evnt,token,str(value)])
            self.checks.append(check)
            return check

        def add_expression_to_checklist(self, expression):
            check = self.ChecklistElement(type="expression", args=[str(expression)])
            self.checks.append(check)
            return check

        def add_sequence_to_checklist(self, sequence: list):
            if type(sequence) != list: raise Exception("Expected sequence type list. Input received: " + str(type(sequence)))
            for e in sequence:
                if type(e) != self.ChecklistElement:
                    raise Exception("Expected list of type ChecklistElement.")
            #
            check = self.ChecklistElement(type="sequence", args=sequence)
            self.checks.append(check)

        def add_undesired_to_checklist(self, undesired):
            # Find undesired elements in checklist. Mark true so they are not checked.
            for i in range(len(self.checks)):
                if self.checks[i] == None: continue
                #
                if self.checks[i].contains(str(undesired)):
                    self.checks[i] = None
            #
            check = self.ChecklistElement(type="undesired", args=[str(undesired)])
            self.checks.append(check)
        
    # --------------------------------------------------------------------------------- #
    
        def validate_event_status(self, event_message):
            # VALIDATE basic format.
            DATA_VALUES_SCHEMA = {
                "type" : "object", "minProperties": 3,
                "properties" : {
                    "code": {"type": "number"},
                    "message": {"type": "string"},
                    "details": {"type": "string"}
                }
            }
            MessagesRecord.validateJson(jsonData=event_message, schema=DATA_VALUES_SCHEMA)
            print("validated: " + str(event_message))
            
    # --------------------------------------------------------------------------------- #
    
        def validate_event_audioPacketStats(self, event_message):
            # VALIDATE basic format.
            DATA_VALUES_SCHEMA = {
                "type" : "object", "minProperties": 3,
                "properties" : {
                    "firstPacketTime": {"pattern": ".+"},
                    "lastPacketTime": {"pattern": ".+"},
                    "audioDurationMs": {"type": "number"}
                }
            }
            MessagesRecord.validateJson(jsonData=event_message, schema=DATA_VALUES_SCHEMA)
            print("validated: " + str(event_message))
                       
    # --------------------------------------------------------------------------------- #
    ## This is emergency temperary workaround due to the last minute change. It works. ##
    
        def validate_event_audioPacketValue(self, event_message, data_pair):
            MessagesRecord.validateValue(event_message, data_pair)
            print("validated: " + str(event_message))
                       
    # --------------------------------------------------------------------------------- #
    
        def validate_event(self, event_message):
            if None == self.chan_id: self.chan_id = event_message["CHAN"]
            # VALIDATE basic format.
            DATA_VALUES_SCHEMA = {
                "type" : "object", "minProperties": 5,
                "properties" : {
                    "TIME": {"type": "string", "pattern": "^[0-9]{17,17}$"},
                    "CHAN": {"const": self.chan_id},
                    "EVNT": {"type": "string", "pattern": "^[A-Za-z]{1,8}$"},
                    "UCPU": {"type": "string"},
                    "SCPU": {"type": "string"}
                }
            }
            MessagesRecord.validateJson(jsonData=event_message, schema=DATA_VALUES_SCHEMA)

            print("validated: " + str(event_message))
            # For every checklist element, if the call log verifies the element, set the element to None (ie. eliminate it from the checklist)
            for i in range(len(self.checks)):
                check = self.checks[i]
                if check != None:
                    validation_result = check.validate(str(event_message))
                    if validation_result == True: self.checks[i] = None

        def close(self, req_nbre):
            """
            Verify checklist elements have all been validated.
            If a check was not updated to True during the messages validation, it will raise an Exception here.
            """
            error_message = ""
            for check in self.checks: 
                if check != None and check.type != "undesired":        
                    error_message += "Unable to validate " + str(check) + " in NRC Recognition Request #" + str(req_nbre) + ".\n"
            
            # At end of validation if error_message has an expression --> raise Exception.
            return error_message

    # ---------------------------------------------------------------------------- #
    
        class ChecklistElement:
            def __init__(self, type, args) -> None:
                self.type = type
                self.args = args
            
            def validate(self, message_val) -> bool:
                if self.type == "undesired":
                    # If args[0] present in message, raise exception
                    if self.assertInExpression(expression=message_val, sub=self.args[0]):
                        raise Exception("Test case expects '" + self.args[0] + "' not in call log messages, but found in actual call log result: " + message_val)
                            
                elif self.type == "value":
                    # value of token args[0] should be args[1].
                    if self.args[0] in message_val:
                        val = self.extract_attribute_value(message_val=message_val, attribute=self.args[0], safe=True)
                        if self.assertInExpression(expression=val, sub=self.args[1]):
                            return True
                
                elif self.type == "token":
                    # if message has EVNT=args[0], token args[1] should be present. Value should contain args[2] (regex).
                    evnt_val = self.extract_attribute_value(message_val=message_val, attribute="EVNT")
                    if evnt_val == self.args[0]:
                        val = self.extract_attribute_value(message_val=message_val, attribute=self.args[1], safe=True)
                        #
                        if self.assertInExpression(expression=val, sub=self.args[2]):
                            return True
                
                elif self.type == "expression":
                    # check if args[0] present in message.
                    if self.assertInExpression(expression=message_val, sub=self.args[0]):
                        return True
                
                elif self.type == "sequence":
                    # recursively validate sub_checks (args[0] -> args[len-1]) and verify that the checks are in order
                    for i in range(len(self.args)):
                        curr_check = self.args[i]
                        prev_check = None if i == 0 else self.args[i - 1]
                        if curr_check == None: continue
                        # step 1) validate
                        validation_result = curr_check.validate(message_val)
                        if validation_result == True:
                            # step 2) make sure prev is already validated
                            if prev_check != None:
                                raise Exception("Sequence not respected: " + str(curr_check) + " occured before " + str(prev_check))
                            # remove curr_check
                            self.args[i] = None

                    # if last element in list is None --> sequence was completed
                    if self.args[-1] == None:
                        return True
                
                else:
                    raise Exception("Checklist element not supported by test harness: " + self.type + ".\n" +
                                    "Expected: value, token, expression, sequence, undesired.")

            def __str__(self) -> str:
                str_rep = self.type + ": "
                for arg in self.args:
                    if arg == None:
                        str_rep += "[None],"
                    elif type(arg) == self.__class__:
                        str_rep += "[" + str(arg) + "],"
                    else:
                        str_rep += arg + ","
                str_rep = str_rep[:-1]
                return str_rep
            
            def contains(self, sub) -> bool:
                # For sequence, check recursively if sub-checks contain undesired expression
                if self.type == "sequence":
                    for check in self.args:
                        if check.contains(sub):
                            return True
                else:
                    for arg in self.args:
                        if self.assertInExpression(expression=arg, sub=sub):
                            return True
                return False

            @staticmethod
            def extract_attribute_value(message_val, attribute, safe=False):
                """ Helper extracts attribute's value from message """
                # Extract substring between 2 markers: <xmlTarget> and </xmlTarget> 
                match_obj = re.search('\'' + attribute + '\': \'(.+?)\'(,|})', message_val)

                # If no result found, raise exception.
                if not match_obj:
                    if safe:
                        return ""
                    else:
                        raise Exception("No " + attribute + " attribute found in: " + message_val)
                    
                # return content as string
                return str(match_obj.group(1))

            @staticmethod
            def assertInExpression(expression, sub):
                """ Helper verifies if sub-expression is inside expression """
                if sub in expression:
                    return True
                #
                pattern = re.compile(sub)
                ret = pattern.search(expression)
                #
                if ret:
                    # check passed, return True
                    return True
                else:
                    # check failed, return False
                    return False
