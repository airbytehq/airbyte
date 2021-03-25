/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.debezium.engine.ChangeEvent;
import io.debezium.engine.DebeziumEngine;
import io.debezium.engine.format.Json;
import java.util.Iterator;
import java.util.Properties;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DPostgresSource {

  private static final Logger LOGGER = LoggerFactory.getLogger(DPostgresSource.class);

  // public static Properties getProps() {
  // // Define the configuration for the Debezium Engine with MySQL connector...
  // // final Properties props = config.asProperties();
  // final Properties props = new Properties();
  // props.setProperty("name", "engine");
  // props.setProperty("plugin.name", "pgoutput");
  // props.setProperty("connector.class", "io.debezium.connector.postgresql.PostgresConnector");
  // props.setProperty("offset.storage", "org.apache.kafka.connect.storage.FileOffsetBackingStore");
  // props.setProperty("offset.storage.file.filename", "/tmp/offsets-" +
  // RandomStringUtils.randomAlphabetic(5) + ".dat");
  // props.setProperty("offset.flush.interval.ms", "60000");
  // /* begin connector properties */
  // // .with("database.server.name", "orders")
  // // .with("database.hostname", "localhost")
  // // .with("database.port", 5432)
  // // .with("database.user", "postgres")
  // // .with("database.password", "postgres")
  // // .with("database.dbname", "demo")
  // // .with("table.whitelist", "public.orders")
  //
  // // https://debezium.io/documentation/reference/configuration/avro.html
  // props.setProperty("key.converter.schemas.enable", "false");
  // props.setProperty("value.converter.schemas.enable", "false");
  //
  // // https://debezium.io/documentation/reference/configuration/event-flattening.html
  // props.setProperty("delete.handling.mode", "rewrite");
  // props.setProperty("drop.tombstones", "false");
  // props.setProperty("transforms.unwrap.type", "io.debezium.transforms.ExtractNewRecordState");
  //
  // props.setProperty("table.include.list", "public.*");
  // props.setProperty("name", "orders-postgres-connector");
  // props.setProperty("include_schema_changes", "true");
  // props.setProperty("database.server.name", "orders");
  // props.setProperty("database.hostname", "localhost");
  // props.setProperty("database.port", "5432");
  // props.setProperty("database.user", "postgres");
  // props.setProperty("database.password", "");
  // props.setProperty("database.dbname", "debezium_test");
  // props.setProperty("database.history", "io.debezium.relational.history.FileDatabaseHistory"); //
  // todo: any reason not to use in memory version and
  // // reload from
  // props.setProperty("database.history.file.filename", "/tmp/debezium/dbhistory-" +
  // RandomStringUtils.randomAlphabetic(5) + ".dat");
  //
  // props.setProperty("slot.name", "debezium");
  //
  // // can set value.converter.schemas.enabled to false if we want to save space/effort for records
  //
  // //
  // https://debezium.io/documentation/reference/1.0/connectors/postgresql.html#discrepance-between-plugins
  //
  // // https://debezium.io/blog/2020/02/25/lessons-learned-running-debezium-with-postgresql-on-rds/
  //
  // return props;
  // }

  // public static void main(String[] args) throws IOException, InterruptedException {
  //
  // BlockingQueue<JsonNode> queue = new LinkedBlockingQueue<>();
  // AtomicReference<Throwable> thrownError = new AtomicReference<>();
  // AtomicBoolean completed = new AtomicBoolean(false);
  // ExecutorService executor = Executors.newSingleThreadExecutor();
  //
  // // Create the engine with this configuration ...
  // try(AutoCloseableIterator<JsonNode> iterator = getIterator(getProps(), queue, completed,
  // thrownError, executor)) {
  // while(iterator.hasNext()) {
  // LOGGER.info("iterator.next() = " + iterator.next());
  // }
  // } catch (Exception e) {
  // throw new RuntimeException(e);
  // }
  //
  // // Do something else or wait for a signal or an event
  // // Engine is stopped when the main code is finished
  // }

  // todo: https://debezium.io/documentation/reference/configuration/event-flattening.html

  // todo: REPLICA IDENTITY for 'public.id_and_name' is 'DEFAULT'; UPDATE and DELETE events will
  // contain previous values only for PK columns

  public static AutoCloseableIterator<JsonNode> getIterator(Properties props,
                                                            BlockingQueue<JsonNode> queue,
                                                            AtomicBoolean completed,
                                                            AtomicReference<Throwable> thrownError,
                                                            ExecutorService executor) {
    DebeziumEngine<ChangeEvent<String, String>> engine = DebeziumEngine.create(Json.class)
        .using(props)
        .notifying(record -> {
          try {
            System.out.println("record = " + record);
            JsonNode node = Jsons.jsonNode(
                ImmutableMap.of("key", record.key() != null ? record.key() : "null", "value", record.value(), "destination", record.destination())); // todo:
                                                                                                                                                     // better
                                                                                                                                                     // transformation
                                                                                                                                                     // function
                                                                                                                                                     // here
            System.out.println("node = " + node);
            queue.add(node);
          } catch (Exception e) {
            System.out.println("error");
            thrownError.set(e);
          }
        })
        // .using((success, message, error) -> {
        // System.out.println("completed!");
        // completed.set(true);
        // thrownError.set(error);
        // })
        .build();

    // Run the engine asynchronously ...
    executor.execute(engine);

    Iterator<JsonNode> delegateIterator = queue.iterator();

    return new AutoCloseableIterator<>() {

      @Override
      public void close() throws Exception {
        System.out.println("in close()");
        engine.close();
        executor.shutdown();

        if (thrownError.get() != null) {
          throw new RuntimeException(thrownError.get());
        }
      }

      @Override
      public boolean hasNext() {
        while (!completed.get()) {
          if (delegateIterator.hasNext()) {
            return true;
          } else {
            System.out.println("sleeping...");
            try {
              Thread.sleep(1000);
            } catch (InterruptedException e) {
              e.printStackTrace();
            }
          }
        }

        return false;
      }

      // todo: how to handle locking?

      @Override
      public JsonNode next() {
        System.out.println("in next()");
        return delegateIterator.next();
      }

    };
  }

}
