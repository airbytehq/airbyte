/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static org.mockito.Mockito.mock;

import com.google.cloud.bigquery.BigQuery;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.DestinationConfig;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.base.destination.typing_deduping.NoopTyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryV1V2Migrator;
import io.airbyte.integrations.destination.bigquery.uploader.AbstractBigQueryUploader;
import io.airbyte.integrations.standardtest.destination.PerStreamStateMessageTest;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.util.Collections;
import java.util.Map;
import java.util.function.Consumer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
public class BigQueryRecordConsumerTest extends PerStreamStateMessageTest {

  @Mock
  private Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap;
  @Mock
  private Consumer<AirbyteMessage> outputRecordCollector;

  private BigQueryRecordConsumer bigQueryRecordConsumer;

  @BeforeEach
  public void setup() {
    DestinationConfig.initialize(Jsons.deserialize("{}"));

    ParsedCatalog parsedCatalog = new ParsedCatalog(Collections.emptyList());
    BigQueryV1V2Migrator migrator = Mockito.mock(BigQueryV1V2Migrator.class);
    bigQueryRecordConsumer = new BigQueryRecordConsumer(
        mock(BigQuery.class),
        uploaderMap,
        outputRecordCollector,
        "test-dataset-id",
        new NoopTyperDeduper(),
        parsedCatalog);
  }

  @Override
  protected Consumer<AirbyteMessage> getMockedConsumer() {
    return outputRecordCollector;
  }

  @Override
  protected FailureTrackingAirbyteMessageConsumer getMessageConsumer() {
    return bigQueryRecordConsumer;
  }

}
