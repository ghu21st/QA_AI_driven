# Test Kafka producer fr
import os

from kafka import KafkaProducer, KafkaConsumer, TopicPartition
from kafka.errors import KafkaError

import json
import time






"""
Create NRC KafkaConsumer instance (current position at last message)
@return: (KafkaConsumer Object, TopicPartition Object)
"""
def create_consumer():
    # topic for Kafka testing
    test_topic = 'QA-test1'
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

    print("Current TopicPartition: " + str(topic_partition))
    print("Current position: " + str(consumer.position(topic_partition)))

    return consumer, topic_partition



"""
Produce messages in topic partition
"""
def produce_messages(text):
    KAFKA_HOSTS = os.getenv("KAFAKA_HOSTS", "mtl-nraas-vm20:31090")
    TOPIC = 'QA-test1'

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_HOSTS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')    # used to convert user-supplied message values to bytes
    )

    for i in range(5):
        data = {text: i}
        print("Send data: {}".format(data))
        future = producer.send(TOPIC, data)
        time.sleep(0.25)
        #
        try: 
            record_metadata = future.get(timeout=5)
        except KafkaError as e:
            print(e)
            pass

        print("topic:\t" + str(record_metadata.topic))
        print("partition:\t" + str(record_metadata.partition))
        print("offset:\t" + str(record_metadata.offset))
    #
    producer.flush()
    producer.close()
    # Delete KafkaProducer instance
    del producer



"""
KafkaConsumer consumes all new messages until latest.
"""
def consume_new_messages(consumer, topic_partition):
    startOffset = consumer.position(topic_partition)
    # Get end offset
    consumer.seek_to_end(topic_partition)
    lastOffset = consumer.position(topic_partition)
    # Move back to start offset
    consumer.seek(topic_partition, startOffset)
    print("Current position: " + str(consumer.position(topic_partition)))
    print("Will read messages from " + str(startOffset) + " to " + str(lastOffset - 1))

    try:
        for message in consumer:
            print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                    message.offset, message.key,
                                                    message.value))
            if message.offset == lastOffset - 1: break
            time.sleep(0.25)
    except KeyboardInterrupt:
        pass



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
Delete KafkaConsumer safely
"""
def delete_consumer(consumer):
    consumer.close(autocommit=True)
    del consumer



################################ LOGIC ENTRY POINT ################################
# Step 1) Create NRC KafkaConsumer instance (current position at last message)
# Step 2) For every production requests
        # a) Produce messages in topic partition.
        # b) KafkaConsumer consumes all new messages until latest.
# Step 3) Delete KafkaConsumer



# Step 1) Create NRC KafkaConsumer instance (current position at last message)
consumer, topic_partition = create_consumer()
print_details(consumer)

# Step 2) For every production requests
# a) Produce messages in topic partition.
# b) KafkaConsumer consumes all new messages until latest.
produce_messages(text="uno")
consume_new_messages(consumer, topic_partition)
print()

produce_messages(text="dos")
consume_new_messages(consumer, topic_partition)
print()

# Step 3) Delete KafkaConsumer
delete_consumer(consumer)