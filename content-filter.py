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

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.stderr.write(
            'Usage: %s <bootstrap-brokers> <requestTopic> <responseTopic>\n' % sys.argv[0])
        sys.exit(1)

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
    # Optional per-message delivery callback (triggered by poll() or flush())
    # when a message has been successfully delivered or permanently
    # failed delivery (after retries).

    def delivery_callback(err, msg):
        if err:
            sys.stderr.write('%% Message failed delivery: %s\n' % err)
        else:
            sys.stderr.write('%% Message delivered to %s [%d] @ %d\n' %
                             (msg.topic(), msg.partition(), msg.offset()))

    try:
        while True:
            msg = c.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                # Proper message
                sys.stderr.write('%% %s [%d] at offset %d with key %s:\n' %
                                 (msg.topic(), msg.partition(), msg.offset(),
                                  str(msg.key())))
                print(msg.value())
                msgJson = json.loads(msg.value())
                msgJson["enriched"] = "wohoo"
                if "removeme" in msgJson:
                    msgJson.pop("removeme")
                try:
                    # Produce line (without newline)
                    p.produce(responseTopic, json.dumps(msgJson),
                              callback=delivery_callback)

                except BufferError:
                    sys.stderr.write('%% Local producer queue is full (%d messages awaiting delivery): try again\n' %
                                     len(p))

                # Serve delivery callback queue.
                # NOTE: Since produce() is an asynchronous API this poll() call
                #       will most likely not serve the delivery callback for the
                #       last produce()d message.
                p.poll(0)

    except KeyboardInterrupt:
        sys.stderr.write('%% Aborted by user\n')

    finally:
        # Close down consumer to commit final offsets.
        c.close()

    # Wait until all messages have been delivered
    sys.stderr.write('%% Waiting for %d deliveries\n' % len(p))
    p.flush()
