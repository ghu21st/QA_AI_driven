import os

from kafka import KafkaConsumer, TopicPartition
from kafka.errors import KafkaError

import json
import time
import re





"""
Create NRC KafkaConsumer instance (current position at last message)
@return: (KafkaConsumer Object, TopicPartition Object)
"""
def create_consumer():
    # topic for Kafka testing
    test_topic = 'nrc-calllog'
    # client_id, This string is passed in each request to servers and can be used to identify specific server-side log entries that correspond to this client
    client_id = 'QA_client'
    # group_id, The name of the consumer group to join for dynamic partition assignment (if enabled), and to use for fetching and committing offsets. If None, auto-partition assignment (via group coordinator) and offset commits are disabled. Default: None
    group_id = None
    # Kafka bootstrap servers & ports to contact to obtain metadata.
    bootstrap_servers = 'mtl-nraas-vm20:31090'
    # fetch from the beginning of the topic/partition (earliest) if the consumer group does not have a committed offset. Or 'latest' for newest message
    auto_offset_reset='latest'
    # Makes sure consumer commits read offset every interval.
    enable_auto_commit=True
    # StopIteration if no message after 10sec
    consumer_timeout_ms=10000
    # get consumer
    consumer = KafkaConsumer(
        group_id=group_id,
        bootstrap_servers=[bootstrap_servers],
        auto_offset_reset=auto_offset_reset,
        enable_auto_commit=enable_auto_commit,
        consumer_timeout_ms=consumer_timeout_ms,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))  # used to convert user-supplied message values to bytes, consume json message
    )
    topic_partition = TopicPartition(test_topic, 0)
    consumer.assign([topic_partition])
    #
    print("Current TopicPartition: " + str(topic_partition))
    print("Current position: " + str(consumer.position(topic_partition)))
    #
    return consumer, topic_partition



"""
Produce messages in topic partition by running smoke test script
"""
def produce_messages():
    for i in range(5):
        os.system("cd ..; sh smoke_nrc_test.sh")



"""
Helper function, prints details on consumer
"""
def print_details(consumer):
    print()
    # Print consumer topics.
    msg_topics = consumer.topics()
    print("Consumer topics: ", msg_topics)
    # check/print current subscribed topics for consumer
    subscribed_topics = consumer.subscription()
    print("Test consumer subscribed topic: ", subscribed_topics)
    # check/print current assigned topic partition for consumer
    assigned_topics = consumer.assignment()
    print("Test consumer assigned topic: ", assigned_topics)
    # offsets of the given partitions.
    offsets = consumer.end_offsets(assigned_topics)
    print(offsets)
    print()



"""
Helper function extracts attribute's value from message
@return string
"""
def extract_attribute_value(message_val, attribute):
    # Extract substring between 2 markers: <xmlTarget> and </xmlTarget> 
    match_obj = re.search('\'' + attribute + '\': \'(.+?)\'', message_val)

    # If no result found, raise exception.
    if not match_obj:
        raise Exception("No " + attribute + " attribute found in: " + message_val)
        
    # return content as string
    return str(match_obj.group(1))


"""
Helper function verifies if expression is inside message value
@return True if expression is in message, False otherwise
"""
def assertInMessage(message_val, expression):
    pattern = re.compile(expression)
    ret = pattern.search(message_val)
    #
    if ret:
        # check passed, return True
        return True
    else:
        # check failed, return False
        return False



"""
Delete KafkaConsumer safely
"""
def delete_consumer(consumer):
    consumer.close(autocommit=True)
    del consumer



"""
Consume messages from the newest to older
"""
def consume_messages_backward():
    # Step 1) Run 5 NRC recognition requests
    produce_messages()

    # Step 2) Create KafkaConsumer positioned at the end of partition. Backtrack messages until 3rd different CHAN id. While still same CHAN id, continue to consume messages and Extract SWIclst, SWIrslt, SWIclnd 
    consumer, topic_partition = create_consumer()
    print_details(consumer)
    print()

    currOffset = consumer.position(topic_partition) - 1
    consumer.seek(topic_partition, currOffset)

    output = []
    prev_chan_id = ""
    recog_calls_cnt = 0

    while(recog_calls_cnt <= 3):
        # Use iterable consumer object to get message at current offset position
        message = next(consumer)
        print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition, message.offset, message.key, message.value))
        message_val = str(message.value)
        
        # Extract id & check with prev_chan_id
        curr_chan_id = extract_attribute_value(message_val=message_val, attribute="CHAN")
        if curr_chan_id != prev_chan_id: 
            prev_chan_id = curr_chan_id
            recog_calls_cnt += 1
            print("\n\n")
        #
        if recog_calls_cnt == 3:
            if (assertInMessage(message_val=message_val, expression="SWIclst") or
                assertInMessage(message_val=message_val, expression="SWIclnd") or 
                assertInMessage(message_val=message_val, expression="SWIrslt")):
                output.append(message_val)
        #
        currOffset -= 1
        consumer.seek(topic_partition, currOffset)
        # Sleep so messages appear sequentially
        time.sleep(0.1)


    # Step 3) Delete KafkaConsumer
    delete_consumer(consumer)

    # Step 4) Print Result
    print("\n##################################\nOUTPUT:")
    for o in output: print(o)



"""
Consume messages from oldest to newer
"""
def consume_messages_forward():
    # Step 1) Create KafkaConsumer positioned at the end of partition.
    consumer, topic_partition = create_consumer()
    print_details(consumer)
    print()

    # Step 2) Run 5 NRC recognition requests
    produce_messages()

    # Step 3) Consume messages until 3rd different CHAN id. While still same CHAN id, continue to consume messages and Extract SWIclst, SWIrslt, SWIclnd 
    startOffset = consumer.position(topic_partition)
    # Get end offset
    consumer.seek_to_end(topic_partition)
    lastOffset = consumer.position(topic_partition)
    # Move back to start offset
    consumer.seek(topic_partition, startOffset)
    print("\n#####################################")
    print("Current offset: " + str(consumer.position(topic_partition)))
    print("Will read messages from " + str(startOffset) + " to " + str(lastOffset - 1))
    print("#####################################\n")
    time.sleep(2)

    output = []
    prev_chan_id = ""
    recog_calls_cnt = 0

    for message in consumer:
        # Use iterable consumer object to get message at current offset position
        print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition, message.offset, message.key, message.value))
        message_val = str(message.value)
        
        # Extract id & check with prev_chan_id
        curr_chan_id = extract_attribute_value(message_val=message_val, attribute="CHAN")
        if curr_chan_id != prev_chan_id: 
            prev_chan_id = curr_chan_id
            recog_calls_cnt += 1
            print("\n\n")
        #
        if recog_calls_cnt == 3:
            if (assertInMessage(message_val=message_val, expression="SWIclst") or
                assertInMessage(message_val=message_val, expression="SWIclnd") or 
                assertInMessage(message_val=message_val, expression="SWIrslt")):
                output.append(message_val)
        
        if message.offset == lastOffset - 1: break
        # Sleep so messages appear sequentially
        time.sleep(0.1)


    # Step 4) Delete KafkaConsumer
    delete_consumer(consumer)

    # Step 5) Print Result
    print("\n##################################\nOUTPUT:")
    for o in output: print(o)



consume_messages_forward()
#consume_messages_backward()