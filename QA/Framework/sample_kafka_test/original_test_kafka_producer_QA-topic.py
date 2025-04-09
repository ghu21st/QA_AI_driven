# Test Kafka producer fr
import os

from kafka import KafkaProducer
from kafka.errors import KafkaError

import json
import time

KAFKA_HOSTS = os.getenv("KAFAKA_HOSTS", "mtl-nraas-vm20:31090")
TOPIC = 'QA-test1'

producer = KafkaProducer(
    bootstrap_servers=KAFKA_HOSTS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')    # used to convert user-supplied message values to bytes
)

data = {
    "timestamp": "2021-05-14T14:25:10.123456",
    "ip": "127.0.0.1",
    "user": "QA1",
    "activities": "testing"
}

for i in range(5):
    future = producer.send(TOPIC, data)
    print("Send data: {}".format(data))
    time.sleep(1)
    #
    try: 
        record_metadata = future.get(timeout=5)
    except KafkaError as e:
        print(e)
        pass
    
    print("\n")
    print(record_metadata.topic)
    print(record_metadata.partition)
    print(record_metadata.offset)

#
producer.flush()
producer.close()
