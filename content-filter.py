#!/usr/bin/env python
#
# Copyright 2016 Confluent Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#
# Example Kafka Producer.
# Reads lines from stdin and sends to Kafka.
#

from confluent_kafka import Producer, Consumer, KafkaException
import sys
import logging
import json
import os

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.stderr.write(
            'Usage: %s <bootstrap-brokers> <requestTopic> <responseTopic>\n' % sys.argv[0])
        sys.exit(1)

    # os.environ["KAFKA_BROKER"]
    # os.environ["FILTER_REQUEST_TOPIC"]
    # os.environ["FILTER_RESPONSE_TOPIC"]

    broker = sys.argv[1]
    requestTopic = sys.argv[2]
    responseTopic = sys.argv[3]

    # Producer configuration
    # See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
    confp = {'bootstrap.servers': broker}
    confc = {'bootstrap.servers': broker, 'group.id': 'something', 'session.timeout.ms': 6000,
             'auto.offset.reset': 'earliest'}
    # Create Producer instance
    p = Producer(**confp)

    logger = logging.getLogger('consumer')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)-15s %(levelname)-8s %(message)s'))
    logger.addHandler(handler)
    # Create Consumer instance
    # Hint: try debug='fetch' to generate some log messages
    c = Consumer(confc, logger=logger)
    c.subscribe([requestTopic])
    logger.info("Content filter started. Waiting for messages on topic '%s'...", requestTopic)
    # Optional per-message delivery callback (triggered by poll() or flush())
    # when a message has been successfully delivered or permanently
    # failed delivery (after retries).

    def delivery_callback(err, msg):
        if err:
            logger.error("Message failed delivery: %s", err)
        else:
            logger.info("Message delivered to topic '%s' [%d] @ %d:\n%s", 
                msg.topic(), msg.partition(), msg.offset(), msg.value().decode('utf-8'))

    try:
        while True:
            msg = c.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                # Process message
                logger.info("Process message from topic '%s' [%d] @ %d with key '%s':\n%s", 
                    msg.topic(), msg.partition(), msg.offset(), str(msg.key()), msg.value().decode('utf-8'))
                try:
                    msgJson = json.loads(msg.value())

                    #msgJson["enriched"] = "wohoo"
                    if "removeme" in msgJson:
                        msgJson.pop("removeme")
                    try:
                        result = json.dumps(msgJson).encode('utf-8')
                        logger.debug("Send message to topic '%s': %s", responseTopic, result.decode('utf-8'))
                        # Produce line (without newline)
                        p.produce(responseTopic, result, callback=delivery_callback)

                    except BufferError:
                        logger.error("Local producer queue is full (%d messages awaiting delivery): try again", len(p))

                except json.decoder.JSONDecodeError:
                    logger.error("Failed to decode JSON message '%s'!", msg.value().decode('utf-8'))

                # Serve delivery callback queue.
                # NOTE: Since produce() is an asynchronous API this poll() call
                #       will most likely not serve the delivery callback for the
                #       last produce()d message.
                p.poll(0)

    except KeyboardInterrupt:
        logger.error('Aborted by user!')

    finally:
        # Close down consumer to commit final offsets.
        c.close()

    # Wait until all messages have been delivered
    logger.info('Waiting for %d deliveries', len(p))
    p.flush()
