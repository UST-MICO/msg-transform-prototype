# Content Filter / Enricher

## Usage

**Docker build:**
```bash
docker build -t content-filter .
docker run -it --rm --name my-running-app content-filter
```

## Commands

### Kafka

**Windows:**

```cmd
.\bin\kafka-topics.bat --list --bootstrap-server localhost:9092
.\bin\kafka-topics.bat --create --bootstrap-server localhost:9092 --topic filter-request --partitions 1 --replication-factor 1
.\kafka-topics.bat --create --bootstrap-server localhost:9092 --topic filter-response --partitions 1 --replication-factor 1

.\bin\kafka-console-producer.bat --bootstrap-server localhost:9092 --topic filter-request
.\bin\kafka-console-consumer.bat --bootstrap-server localhost:9092 --topic filter-response
```

**Linux:**

Start Zookeeper:
```bash
./bin/zookeeper-server-start.sh ./config/zookeeper.properties
```

Start Kafka:
```bash
./bin/kafka-server-start.sh ./config/server.properties
```

```bash
./kafka-topics.sh --list --bootstrap-server localhost:9092
./kafka-topics.sh --create --bootstrap-server localhost:9092 --topic filter-request --partitions 1 --replication-factor 1
./kafka-topics.sh --create --bootstrap-server localhost:9092 --topic filter-response --partitions 1 --replication-factor 1

./kafka-console-producer.sh --broker-list localhost:9092 --topic filter-request
./kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic filter-response
```

## Example

```json
{
    "specversion": "0.2",
    "type": "com.example.someevent",
    "source": "/mycontext",
    "id": "A234-1234-1234",
    "time": "2018-04-05T17:31:00Z",
    "comexampleextension1": "value",
    "comexampleextension2": {
        "otherValue": 5
    },
    "contenttype": "text/xml",
    "data": "<much wow=\"xml\"/>",
    "removeme": "wowlol"
}
```
