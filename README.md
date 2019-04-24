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

Start ZooKeeper:
```powershell
.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
```

Start Kafka:
```powershell
.\bin\windows\kafka-server-start.bat .\config\server.properties
```

Topics (list and create):
```powershell
.\bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092
.\bin\windows\kafka-topics.bat --create --bootstrap-server localhost:9092 --topic filter-request --partitions 1 --replication-factor 1
.\bin\windows\kafka-topics.bat --create --bootstrap-server localhost:9092 --topic filter-response --partitions 1 --replication-factor 1
```

Messages (produce and consume):
```console
.\bin\windows\kafka-console-producer.bat --broker-list localhost:9092 --topic filter-request
.\bin\windows\kafka-console-consumer.bat --bootstrap-server localhost:9092 --topic filter-response
```

**Linux:**

Start Zookeeper:
```console
./bin/zookeeper-server-start.sh ./config/zookeeper.properties
```

Start Kafka:
```console
./bin/kafka-server-start.sh ./config/server.properties
```

Topics (list and create):
```console
./bin/kafka-topics.sh --list --bootstrap-server localhost:9092
./bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --topic filter-request --partitions 1 --replication-factor 1
./bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --topic filter-response --partitions 1 --replication-factor 1
```

Messages (produce and consume):
```console
./bin/kafka-console-producer.sh --broker-list localhost:9092 --topic filter-request
./bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic filter-response
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
