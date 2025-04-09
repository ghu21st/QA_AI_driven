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

for i in range(10):
    data = {'number': i}
    print("Send data: {}".format(data))
    future = producer.send(TOPIC, data)
    time.sleep(0.5)
    #
    try: 
        record_metadata = future.get(timeout=5)
    except KafkaError as e:
        print(e)
        pass

    print("topic:\t" + str(record_metadata.topic))
    print("partition:\t" + str(record_metadata.partition))
    print("offset:\t" + str(record_metadata.offset))
    print()

#
producer.flush()
producer.close()
