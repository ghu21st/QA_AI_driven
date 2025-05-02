import os

from kafka import KafkaConsumer, TopicPartition
from kafka.errors import KafkaError

import json
import time
import yaml
from MessagesRecord import MessagesRecord
import TestContext

class KafkaModule:

    def __init__(self, test_fixture):
        """ Constructs KafkaModule instance with consumer and partition objects. """
        # Initialize messages string to be saved in logs.
        self.messages_string = ""
        self.errors_string = ""
        # Initialize logger
        self.logger = test_fixture
        self.log_file = test_fixture.log_handler.baseFilename

        # If CALL_LOGGING environment variable is not set, skip call logging
        if "CLOG_switch" not in os.environ or os.environ["CLOG_switch"] != "True": return
        # Create Kafka consumer associated to the KafkaModule instance and TopicPartition where it consumes from.
        self.consumer, self.topic_partition, self.startOffset = self.__create_consumer()


    def create_messages_record(self, recogInit, expected_result, result_status="SUCCESS", status_code=200, status_message="OK", secure_clog=False, user_id=None):
        """ Creates an returns new messages-record. """
        return MessagesRecord(recogInit, expected_result, result_status, status_code, status_message, secure_clog, user_id)


    def validate_callLogs(self, records, data_pair=""):
        """ 
        As Kafka messages are consumed, check the record they belong to by the message requestid.
        Perform validation checks on the call logs at every offset.
        Consume all messages and records.
        Write to logs and raise Exception if error found.
        """

        if "CLOG_switch" not in os.environ or os.environ["CLOG_switch"] != "True": return
        #
        if self.startOffset == 0:
            # wait few seconds for environment to be fully initialized
            print("Sleeping for 30s to ensure kafka-client setup")
            time.sleep(30)
        else:
            time.sleep(10)
        #
        if isinstance(records, MessagesRecord):
            records = [records]
        elif isinstance(records, list):
            if len(records) == 0:
                raise Exception("Expected records list as a list with at least 1 element.\n" +
                                "Pass messages records as input to validate_callLogs()")
        else:
            raise Exception("Expected input records list or one MessagesRecord object,\n" +
                            "Invalid input received, input type: " + str(type(records)))

        msg_cnt = 0
        req_cnt = 0
        curr_id = None
        curr_record = records.pop(0)
        curr_record.req_nbre = req_cnt
        lastOffset = self.__get_last_offset()

        try:
            for message in self.consumer:
                msg_id = message.value["data"]["requestid"]
                if curr_id == None: curr_id = msg_id
                msg_cnt += 1

                if curr_id != msg_id:
                    # Messages of new record => close and validate previous record
                    self.errors_string += curr_record.close()
                    self.messages_string += "\n\n"
                    msg_cnt = 1
                    req_cnt += 1
                    # If no next record => fail
                    if len(records) == 0:
                        raise Exception("End of records, some messages remaining.\nVerify number of MessageRecords == number of requests.")
                    # Use next record
                    curr_record = records.pop(0)
                    curr_id = msg_id
                
                # Add new message to logs and validate
                # print("########## REQ {} MSG {} ##########".format(req_cnt, msg_cnt))
                # print(json.dumps(message.value, indent=4))
                self.messages_string += json.dumps(message.value, indent=4) + "\n"
                if data_pair == "":
                    self.errors_string += self.perform_checks(curr_record, message)
                else:
                    self.errors_string += self.perform_checks(curr_record, message, data_pair)

                if message.offset == lastOffset - 1:
                    # Last message reached
                    self.errors_string += curr_record.close()
                    # If records list no exhausted => fail
                    if len(records) > 0:
                        raise Exception("End of messages, some records remaining.\nVerify number of MessageRecords == number of requests.")
                    break

        except KeyboardInterrupt:
            self.errors_string += "\nInterrupted by Keyboard Interrupt"
            # Raise as new KeyboardInterrupt so test case exits safely.
            raise KeyboardInterrupt()
        
        except (KafkaError, Exception) as e:
            self.errors_string += "\n" + str(e)
            # Raise as new Exception so test case FAILS and message displayed.
            raise e
        
        finally:
            # Add messages to log files and print.
            self.__write_to_log(self.messages_string, self.errors_string)
            self.__write_to_callLog(self.messages_string, self.errors_string)
            if self.errors_string != "":
                raise Exception(self.errors_string)
            else:
                print("SUCCESS validation of the call logs!")

        
    def perform_checks(self, curr_record, message, data_pair=""):
        """ 
        Perform message top values checks and additional checks specific to the message dataContentType
        @input: current message record object, Kafka message
        """
        errors_string = ""
        msg_dataContentType = message.value["data"]["dataContentType"]
        
        # General message header checks
        errors_string += curr_record.perform_top_values_checks(message.value)
        
        # TYPE 1: recognitionInit
        if msg_dataContentType == "application/x-nuance-nrc-recognitioninit.v1+json": 
            errors_string += curr_record.perform_recognitionInit_checks(message.value["data"])
        elif msg_dataContentType == "application/x-nuance-nrc-dtmfrecognitioninit.v1+json": 
            errors_string += curr_record.perform_recognitionInit_checks(message.value["data"])
        # TYPE 2: status code and message
        elif msg_dataContentType == "application/x-nuance-nrc-status.v1+json":
            errors_string += curr_record.perform_status_checks(message.value["data"])
        # TYPE 3: start of speech
        elif msg_dataContentType == "application/x-nuance-nrc-startofspeech.v1+json":
            errors_string += curr_record.perform_startOfSpeech_checks(message.value["data"])
        # TYPE 4: end of speech
        elif msg_dataContentType == "application/x-nuance-nrc-endofspeech.v1+json":
            errors_string += curr_record.perform_endOfSpeech_checks(message.value["data"]) 
        # TYPE 5: result
        elif msg_dataContentType == "application/x-nuance-nrc-result.v1+json": 
            errors_string += curr_record.perform_result_checks(message.value["data"])
        # TYPE 6: call summary
        elif msg_dataContentType == "application/x-nuance-nrc-callsummary.v1+json":
            if data_pair == "":
                errors_string += curr_record.perform_callsummary_checks(message.value["data"]) 
            else:
                errors_string += curr_record.perform_callsummary_checks(message.value["data"], data_pair) 
        else:
            raise Exception("Message dataContentType '{}' not expected and not handled.".format(msg_dataContentType))

        return errors_string


    def cleanup(self):
        # If CALL_LOGGING environment variable is not set, skip call logging
        if "CLOG_switch" not in os.environ or os.environ["CLOG_switch"] != "True": return
        self.consumer.close(autocommit=True)
        del self.consumer


    # ---------------------- Helper methods ---------------------- #
    
    def __create_consumer(self):
        """
        Creates NRC KafkaConsumer instance (current position at last message).
        @return: (KafkaConsumer Object, TopicPartition Object, Consumer Start Offset in partition)
        """     

        client_id = 'QA_client' # string passed in each request to servers and can be used to identify specific server-side log entries that correspond to this client
        group_id = None # name of the consumer group to join for dynamic partition assignment (if enabled), and to use for fetching and committing offsets. If None, auto-partition assignment (via group coordinator) and offset commits are disabled. Default: None
        
        # Get config from Framework/config/testServerConfig.yaml
        root_dir = os.path.abspath(__file__)
        for i in range(3):
            root_dir = os.path.dirname(root_dir)
        if os.path.isdir(os.path.join(root_dir, 'Framework')):
            root_dir = os.path.join(root_dir, 'Framework')
        config_file = os.path.join(root_dir, 'config', 'testServerConfig.yaml')
        with open(config_file, 'r') as f:
            config = yaml.load(f)

        # topic for Kafka testing
        x_nuance_client_id = config["NRCTestMetadata"]["x-nuance-client-id"] 
        TEST_TOPIC = x_nuance_client_id.split(":")[1] # 'null' 'mydummyappid2'
        # Kafka bootstrap servers (from config file) & ports to contact to obtain metadata.
        SERVER = str(config["NRCServiceIP"])
        PORT = str(config["NRCKafkaPort"])
        bootstrap_servers = SERVER + ':' + PORT
        
        auto_offset_reset='latest' # fetch from 'latest' for newest message
        enable_auto_commit=False # Makes sure consumer commits read offset every interval.
        consumer_timeout_ms=10000 # StopIteration if no message after 10sec
        
        consumer = KafkaConsumer(
            group_id=group_id,
            bootstrap_servers=[bootstrap_servers],
            auto_offset_reset=auto_offset_reset,
            enable_auto_commit=enable_auto_commit,
            consumer_timeout_ms=consumer_timeout_ms,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),  # used to convert user-supplied message values to bytes, consume json message
        )
        topic_partition = TopicPartition(TEST_TOPIC, 0)
        consumer.assign([topic_partition])
        # Consume messages till end reached end reached
        for _ in consumer: continue
        startOffset = consumer.position(topic_partition)

        return consumer, topic_partition, startOffset


    def __get_last_offset(self):
        """
        Obtains start and last offsets of messages consumer consumes in partition.
        @return: start offset, last offset
        """ 
        startOffset = self.startOffset
        currOffset = self.consumer.position(self.topic_partition)
        # Move to end to get end offset 
        self.consumer.seek_to_end(self.topic_partition)
        lastOffset = self.consumer.position(self.topic_partition)
        # Move back to current offset.
        self.consumer.seek(self.topic_partition, currOffset)
        # print("startOffset: ", startOffset)
        # print("currOffset: ", currOffset)
        # print("lastOffset: ", lastOffset)
        # Verify that there are messages that we can consume.
        if (startOffset >= lastOffset):
            raise Exception("No new messages can be consumed. startOffset=" +
                            str(startOffset) + " and lastOffset=" + str(lastOffset) + ". " + 
                            "Verify test case execution suspended using time.sleep() after recognition request.")
        #
        return lastOffset


    def __write_to_log(self, msgs, errors):
        """
        Helper writes text to most recent log.
        @input: string of concatenated messages to write to logs.
        """
        to_write = (
            "\n\n-------- START of QA test collected call log section --------\n" + msgs +
            "-------- END of QA test collected call log section --------\n" + errors + "\n")
        #
        self.logger.info(to_write)

    
    def __write_to_callLog(self, msgs, errors):
        """
        Helper writes text to most recent callLog.
        @input: string of concatenated messages to write to logs.
        """
        to_write = msgs + errors
        
        # Construct new filename
        name_elements = self.log_file.split(".")
        name_elements.pop()
        new_filename = ""
        for e in name_elements:
            new_filename += e + "."
        new_filename += "callLog"
        #
        with open(new_filename, "a") as f:
            f.write(to_write)
            f.close()
