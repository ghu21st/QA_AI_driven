# note: pip install kafka-python version 2.0 or above
from kafka import KafkaConsumer, TopicPartition
from kafka.errors import KafkaError
import json

import time

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

# subscribe/change a topic
# Note: manually assign partitions via consumer.assign() instead of subscribing to topics via consumer.subscribe(). If you do this, seek_to_beginning() should work as expected.
# consumer.subscribe(topics=['nrc-calllog'], pattern=None, listener=None)

# assign topic partition -----------
# a) manually:
# topic_partition = TopicPartition(test_topic, 0)
# consumer.assign([topic_partition])
# b) automatically:
assignments = [] # Consumer partition assignments list
partitions = consumer.partitions_for_topic(test_topic)
for p in partitions:
    assignments.append(TopicPartition(test_topic, p))
# register topic
consumer.assign(assignments)

# --------------------------------------
# print consumer topics
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

# ----------------------------------
# for tp in assignments:
#     print()
#     print("Current consumer assignment: " + str(tp))
#     # --- get the last offset value
#     # consumer.seek_to_end(tp)
#     lastOffset = consumer.position(tp)
#     print("Test topic last offset value: ", lastOffset)

#     # --- Set kafka seeking to beginning
#     consumer.seek_to_beginning(tp)
#     firstOffset = consumer.position(tp)
#     #
#     try:
#         for message in consumer:
#             print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
#                                                  message.offset, message.key,
#                                                  message.value))
#             # stop the loop once reached the last offset
#             if message.offset == lastOffset - 1:
#                break
#             time.sleep(0.25)
#     #
#     except KeyboardInterrupt:
#         pass
#     #
#     except KafkaError as e:
#         print(e)
#         pass

# print("\nThe first message offset: ", firstOffset)
# print("The last message offset: ", lastOffset - 1)

for tp in assignments:
    print("Current Topic Partition assignment: " + str(tp))
    lastOffset = consumer.position(tp)
    print("current position: " + str(lastOffset))
    consumer.seek_to_beginning(tp)
    print("current position: " + str(consumer.position(tp)))
    

    try:
        for message in consumer:
            print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                    message.offset, message.key,
                                                    message.value))
            if message.offset == lastOffset - 1: break
            time.sleep(0.25)
    except KeyboardInterrupt:
        pass


for tp in assignments:
    print("Current Topic Partition assignment: " + str(tp))
    lastOffset = consumer.position(tp)
    print("current position: " + str(lastOffset))

    try:
        for message in consumer:
            print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                    message.offset, message.key,
                                                    message.value))
            if message.offset == lastOffset - 1: break
            time.sleep(0.25)
    except KeyboardInterrupt:
        pass

consumer.close(autocommit=True)

# consumer.seek(0, 0) =>start reading from the beginning of the queue.
# consumer.seek(0, 1) =>start reading from current offset.
# consumer.seek(0, 2) # =>skip all the pending messages and start reading only new messages
