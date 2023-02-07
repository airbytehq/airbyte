/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.five_gb_benchmark;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.AbstractIterator;
import com.google.common.collect.ImmutableMap;
import com.opencsv.CSVReader;
import com.opencsv.exceptions.CsvValidationException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.io.FileReader;
import java.io.IOException;
import java.net.URISyntaxException;
import java.util.List;
import javax.annotation.CheckForNull;
import org.checkerframework.checker.nullness.qual.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class FiveGbBenchmarkSource extends BaseConnector implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(FiveGbBenchmarkSource.class);

  FiveGbBenchmarkSource() {
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new FiveGbBenchmarkSource();
    LOGGER.info("starting source: {}", FiveGbBenchmarkSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", FiveGbBenchmarkSource.class);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) throws Exception {
    return null;
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode config, final ConfiguredAirbyteCatalog catalog, final JsonNode state)
      throws Exception {

    final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = List.of(
      AutoCloseableIterators.lazyIterator(() -> AutoCloseableIterators.fromIterator(new AirbyteStreamIterator("products")))
    );

    return AutoCloseableIterators
        .appendOnClose(AutoCloseableIterators.concatWithEagerClose(iteratorList), () -> LOGGER.info("Done."));
  }

  private static class AirbyteStreamIterator extends AbstractIterator<AirbyteMessage> {

    private final String streamName;

    public AirbyteStreamIterator(final String streamName) {
      this.streamName = streamName;
    }

    @CheckForNull
    @Override
    protected @Nullable AirbyteMessage computeNext() {
      try (final CSVReader csvReader = new CSVReader(new FileReader(MoreResources.readResourceAsFile(streamName)));) {
        final String[] values = csvReader.readNext();
        if (values != null) {
          return new AirbyteMessage()
              .withType(Type.RECORD)
              .withRecord(new AirbyteRecordMessage().withData(Jsons.jsonNode(ImmutableMap.of(
                  "make", values[0],
                  "year", values[1],
                  "model", values[2],
                  "price", values[3],
                  "created_at", values[4]
                  ))));
        } else {
          return endOfData();

        }
      } catch (final IOException | URISyntaxException | CsvValidationException e) {
        throw new RuntimeException(e);
      }
    }
  }
}
