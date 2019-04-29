# Content Filter / Enricher

## Discussion

* Should there be multiple specialized filters / enrichers?
  * Yes, it's not possible to implement one general-purpose filter / enricher
  * It would make sense to implement a filter / enricher per data source
  * Specialized types of an enricher:
    * Computation
    * Environment
    * Database (e.g. MySQL)
    * Files
    * Other applications / services

* How does a message producer know which filter / enricher is the correct one?
  * A content based router could be the target of a producer that routes the message to the correct filter / enricher.

* Filtering: Blacklist vs. whitelist?
  * Both could be useful depending on the use case
  * Configuration should decide

* Filtering: How to flatten a hierarchy? How to remove a specific property in a nested structure?
  * Flattening and removing properties should be splitted into two steps

* What should be the purpose of an external configuration?
  * Define properties that should be
    * removed (blacklisting)
    * remain unaffected, others will be removed (whitelisting)
    * enriched with data (depending on type of the enricher)
  * Set a specific mode (e.g. whitelisting vs. blacklisting)

* What kind of external configuration should be used? Database? REST API? Environment variables?
  * ->  At first the use of environment variables should be sufficient.

**Example "GenericFilter" in whitelisting mode:**
* Configuration: `{"mode":"WHITELISTING","properties":["important"]}`
* Input: `{"key":"value","important":"value2}`
* Output: `{"important":"value2"}`

**Example "GenericFilter" in blacklisting mode:**
* Configuration: `{"mode":"BLACKLISTING","properties":["removeme"]}`
* Input: `{"key":"value","removeme":"value2}`
* Output: `{"key":"value"}`

**Example "GenericFilter" in flattening mode:**
* Configuration: `{"mode":"FLATTENING"}`
* Input: `{"object1":{"nested1":"value1"},"object2":{"nested2":"value2"}}`
* Output: `{"nested1":"value1","nested2":"value2"}`

**Example "ComputationEnricher":**
* Python `eval` / `exec` can be used, however security concerns must be considered
  * Access to variables and methods can be restricted (e.g. access to `os` must not be allowed)
* Data source: no external data source required, value is directly computed
* Configuration: `{"operations":[{"property":"addition","override":false,"target":"result"}]}`
* Input: `{"addition":"3+5"}`
* Output: `{"addition":"3+5", "result":"8"}`

**Example "EnvironmentEnricher":**
* Data source: environment
* Configuration: `["local_time"]`
* Input: `{"key":"value"}`
* Output: `{"key":"value", "local_time":"2019-04-23T15:43:00Z"}`

**Example "ExternalServiceEnricher":**
* Data source: external service
* Configuration: `{}`
* Input: `[{"api":"http://dummy.restapiexample.com/api/v1/employee/5800","jsonpath":"$.employee_name", "target":"employee_name"}]`
* Output: `[{"employee_name": "mahesh"}]`

## Usage

**Docker build:**
```bash
docker build -t content-filter .
docker run -it --rm --name my-running-app content-filter
```

## Commands

### Docker

**Start Kafka and ZooKeeper:**
```bash
docker-compose up
```

Remove containers and volumes:
```bash
docker-compose rm --force -v
```

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
