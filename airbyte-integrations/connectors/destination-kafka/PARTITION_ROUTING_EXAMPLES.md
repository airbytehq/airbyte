# Kafka Destination Connector - Partition Routing Examples

## Example Configurations

### 1. Single Field Partition Routing

```json
{
  "bootstrap_servers": "localhost:9092",
  "topic_pattern": "orders.{stream}",
  "partition_key_field": "user_id",
  "protocol": {
    "security_protocol": "PLAINTEXT"
  },
  "acks": "1",
  "enable_idempotence": false,
  "compression_type": "none",
  "batch_size": 16384,
  "linger_ms": 0,
  "max_in_flight_requests_per_connection": 5,
  "client_dns_lookup": "use_all_dns_ips",
  "buffer_memory": 33554432,
  "max_request_size": 1048576,
  "retries": 2147483647,
  "socket_connection_setup_timeout_ms": 10000,
  "socket_connection_setup_timeout_max_ms": 30000,
  "max_block_ms": 60000,
  "request_timeout_ms": 30000,
  "delivery_timeout_ms": 120000,
  "send_buffer_bytes": 131072,
  "receive_buffer_bytes": 32768
}
```

**Sample Input Record:**
```json
{
  "user_id": "user123",
  "order_id": "order456",
  "product": "laptop",
  "amount": 999.99
}
```

**Result:** All records with `user_id = "user123"` will go to the same Kafka partition.

---

### 2. Composite Key Partition Routing

```json
{
  "bootstrap_servers": "localhost:9092",
  "topic_pattern": "orders.{stream}",
  "partition_key_field": "user_id,order_id",
  "protocol": {
    "security_protocol": "PLAINTEXT"
  },
  "acks": "1",
  "enable_idempotence": false,
  "compression_type": "none",
  "batch_size": 16384,
  "linger_ms": 0,
  "max_in_flight_requests_per_connection": 5,
  "client_dns_lookup": "use_all_dns_ips",
  "buffer_memory": 33554432,
  "max_request_size": 1048576,
  "retries": 2147483647,
  "socket_connection_setup_timeout_ms": 10000,
  "socket_connection_setup_timeout_max_ms": 30000,
  "max_block_ms": 60000,
  "request_timeout_ms": 30000,
  "delivery_timeout_ms": 120000,
  "send_buffer_bytes": 131072,
  "receive_buffer_bytes": 32768
}
```

**Sample Input Record:**
```json
{
  "user_id": "user123",
  "order_id": "order456",
  "product": "laptop",
  "amount": 999.99
}
```

**Result:** Kafka message key will be `"user123|order456"`. Records with the same combination will go to the same partition.

---

### 3. Nested Field Partition Routing

```json
{
  "bootstrap_servers": "localhost:9092",
  "topic_pattern": "users.{stream}",
  "partition_key_field": "user.id",
  "protocol": {
    "security_protocol": "PLAINTEXT"
  },
  "acks": "1",
  "enable_idempotence": false,
  "compression_type": "none",
  "batch_size": 16384,
  "linger_ms": 0,
  "max_in_flight_requests_per_connection": 5,
  "client_dns_lookup": "use_all_dns_ips",
  "buffer_memory": 33554432,
  "max_request_size": 1048576,
  "retries": 2147483647,
  "socket_connection_setup_timeout_ms": 10000,
  "socket_connection_setup_timeout_max_ms": 30000,
  "max_block_ms": 60000,
  "request_timeout_ms": 30000,
  "delivery_timeout_ms": 120000,
  "send_buffer_bytes": 131072,
  "receive_buffer_bytes": 32768
}
```

**Sample Input Record:**
```json
{
  "user": {
    "id": "user123",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "action": "login",
  "timestamp": "2023-01-01T12:00:00Z"
}
```

**Result:** Kafka message key will be `"user123"`. Records with the same `user.id` will go to the same partition.

---

### 4. Mixed Fields Partition Routing

```json
{
  "bootstrap_servers": "localhost:9092",
  "topic_pattern": "events.{stream}",
  "partition_key_field": "user.id,action,timestamp",
  "protocol": {
    "security_protocol": "PLAINTEXT"
  },
  "acks": "1",
  "enable_idempotence": false,
  "compression_type": "none",
  "batch_size": 16384,
  "linger_ms": 0,
  "max_in_flight_requests_per_connection": 5,
  "client_dns_lookup": "use_all_dns_ips",
  "buffer_memory": 33554432,
  "max_request_size": 1048576,
  "retries": 2147483647,
  "socket_connection_setup_timeout_ms": 10000,
  "socket_connection_setup_timeout_max_ms": 30000,
  "max_block_ms": 60000,
  "request_timeout_ms": 30000,
  "delivery_timeout_ms": 120000,
  "send_buffer_bytes": 131072,
  "receive_buffer_bytes": 32768
}
```

**Sample Input Record:**
```json
{
  "user": {
    "id": "user123",
    "name": "John Doe"
  },
  "action": "purchase",
  "timestamp": "2023-01-01T12:00:00Z",
  "product": "laptop",
  "amount": 999.99
}
```

**Result:** Kafka message key will be `"user123|purchase|2023-01-01T12:00:00Z"`.

---

### 5. Backward Compatibility (No Partition Key)

```json
{
  "bootstrap_servers": "localhost:9092",
  "topic_pattern": "events.{stream}",
  "protocol": {
    "security_protocol": "PLAINTEXT"
  },
  "acks": "1",
  "enable_idempotence": false,
  "compression_type": "none",
  "batch_size": 16384,
  "linger_ms": 0,
  "max_in_flight_requests_per_connection": 5,
  "client_dns_lookup": "use_all_dns_ips",
  "buffer_memory": 33554432,
  "max_request_size": 1048576,
  "retries": 2147483647,
  "socket_connection_setup_timeout_ms": 10000,
  "socket_connection_setup_timeout_max_ms": 30000,
  "max_block_ms": 60000,
  "request_timeout_ms": 30000,
  "delivery_timeout_ms": 120000,
  "send_buffer_bytes": 131072,
  "receive_buffer_bytes": 32768
}
```

**Result:** Uses random UUID keys (existing behavior) for round-robin partitioning.

---

## Test Scenarios

### Scenario 1: Same Key → Same Partition

**Input Records:**
```json
[
  {"user_id": "user123", "order_id": "order1", "product": "laptop"},
  {"user_id": "user123", "order_id": "order2", "product": "mouse"},
  {"user_id": "user123", "order_id": "order3", "product": "keyboard"}
]
```

**Configuration:** `partition_key_field: "user_id"`

**Expected:** All three records go to the same partition.

---

### Scenario 2: Different Keys → Different Partitions

**Input Records:**
```json
[
  {"user_id": "user123", "order_id": "order1", "product": "laptop"},
  {"user_id": "user456", "order_id": "order2", "product": "mouse"},
  {"user_id": "user789", "order_id": "order3", "product": "keyboard"}
]
```

**Configuration:** `partition_key_field: "user_id"`

**Expected:** Records likely go to different partitions.

---

### Scenario 3: Missing Field → Fallback UUID

**Input Records:**
```json
[
  {"order_id": "order1", "product": "laptop"},
  {"order_id": "order2", "product": "mouse"}
]
```

**Configuration:** `partition_key_field: "user_id"`

**Expected:** Both records get random UUID keys (fallback behavior).

---

## Testing with Kafka CLI

### 1. Start Kafka Consumer
```bash
kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic orders.stream --from-beginning --property print.key=true
```

### 2. Send Test Records via Airbyte
Configure your Airbyte connection with one of the example configurations above and run a sync.

### 3. Verify Partition Assignment
```bash
kafka-run-class.sh kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic orders.stream
```

### 4. Check Message Keys
Look at the consumer output to verify that records with the same key value have the same partition assignment.
