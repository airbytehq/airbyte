/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.BigQuery;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser;
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDestinationHandler;
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator;
import io.airbyte.integrations.destination.bigquery.uploader.AbstractBigQueryUploader;
import io.airbyte.integrations.standardtest.destination.PerStreamStateMessageTest;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;

import java.util.Collections;
import java.util.Map;
import java.util.function.Consumer;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.mockito.Mockito.mock;

@ExtendWith(MockitoExtension.class)
public class BigQueryRecordConsumerTest extends PerStreamStateMessageTest {

  @Mock
  private Map<BigQueryRecordConsumer.StreamWriteTargets, AbstractBigQueryUploader<?>> uploaderMap;
  @Mock
  private Consumer<AirbyteMessage> outputRecordCollector;

  private BigQueryRecordConsumer bigQueryRecordConsumer;

  @BeforeEach
  public void setup() {
    bigQueryRecordConsumer = new BigQueryRecordConsumer(
        mock(BigQuery.class),
        uploaderMap,
        outputRecordCollector,
        "test-dataset-id",
        mock(BigQuerySqlGenerator.class),
        mock(BigQueryDestinationHandler.class),
        new CatalogParser.ParsedCatalog(Collections.emptyList()),
        false,
        "test-namespace-override"
    );
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
