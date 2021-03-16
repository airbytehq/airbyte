package io.airbyte.integrations.source.postgres;

import static java.lang.Thread.sleep;

import io.debezium.config.Configuration;
import io.debezium.engine.ChangeEvent;
import io.debezium.engine.DebeziumEngine;
import io.debezium.engine.format.Json;
import java.io.IOException;
import java.util.Properties;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import org.apache.log4j.Level;
import org.apache.log4j.LogManager;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DPostgresSource {
  private static final Logger LOGGER = LoggerFactory.getLogger(DPostgresSource.class);

  public static void main(String[] args) throws IOException, InterruptedException {

    // Define the configuration for the Debezium Engine with MySQL connector...
//    final Properties props = config.asProperties();
    final Properties props = new Properties();
    props.setProperty("name", "engine");
    props.setProperty("plugin.name", "pgoutput");
    props.setProperty("connector.class", "io.debezium.connector.postgresql.PostgresConnector");
    props.setProperty("offset.storage", "org.apache.kafka.connect.storage.FileOffsetBackingStore");
    props.setProperty("offset.storage.file.filename", "/tmp/offsets.dat");
    props.setProperty("offset.flush.interval.ms", "60000");
    /* begin connector properties */
//        .with("database.server.name", "orders")
//        .with("database.hostname", "localhost")
//        .with("database.port", 5432)
//        .with("database.user", "postgres")
//        .with("database.password", "postgres")
//        .with("database.dbname", "demo")
//        .with("table.whitelist", "public.orders")

    props.setProperty("table.whitelist", "public.*");
    props.setProperty("name", "orders-postgres-connector");
    props.setProperty("INCLUDE_SCHEMA_CHANGES", "true");
    props.setProperty("include_schema_changes", "true");
    props.setProperty("database.server.name", "orders");
    props.setProperty("database.hostname", "localhost");
    props.setProperty("database.port", "5432");
    props.setProperty("database.user", "postgres");
    props.setProperty("database.password", "");
    props.setProperty("database.dbname", "debezium_test");
    props.setProperty("database.history", "io.debezium.relational.history.FileDatabaseHistory");
    props.setProperty("database.history.file.filename", "/tmp/debezium/dbhistory.dat");

// Create the engine with this configuration ...
    try (DebeziumEngine<ChangeEvent<String, String>> engine = DebeziumEngine.create(Json.class)
        .using(props)
        .notifying(record -> {
          LOGGER.info(record.toString());
        }).build()
    ) {
      // Run the engine asynchronously ...
      ExecutorService executor = Executors.newSingleThreadExecutor();
      executor.execute(engine);

      while(true) {
        sleep(5000);
//        LOGGER.info("the mummy wakes");
      }

      // Do something else or wait for a signal or an event
    }
// Engine is stopped when the main code is finished
  }

}
