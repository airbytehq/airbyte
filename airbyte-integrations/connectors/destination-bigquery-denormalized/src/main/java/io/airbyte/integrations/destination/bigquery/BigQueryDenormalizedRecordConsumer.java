/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.BigQuery;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.bigquery.BigQueryDestination.UploadingMethod;
import io.airbyte.integrations.destination.bigquery.strategy.BigQueryDenormalizedUploadStandardStrategy;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryDenormalizedRecordConsumer extends BigQueryRecordConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDenormalizedRecordConsumer.class);

  private final Set<String> invalidKeys;
  private final Set<String> fieldsWithRefDefinition;

  public BigQueryDenormalizedRecordConsumer(final BigQuery bigquery,
                                            final Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector,
                                            final StandardNameTransformer namingResolver,
                                            final Set<String> fieldsWithRefDefinition) {
    super(bigquery, writeConfigs, catalog, outputRecordCollector, false, false);
    this.fieldsWithRefDefinition = fieldsWithRefDefinition;
    invalidKeys = new HashSet<>();
    bigQueryUploadStrategyMap.put(UploadingMethod.STANDARD,
        new BigQueryDenormalizedUploadStandardStrategy(bigquery, catalog, outputRecordCollector, namingResolver, invalidKeys,
            Set.copyOf(fieldsWithRefDefinition)));
  }

  @Override
  public void close(final boolean hasFailed) {
    fieldsWithRefDefinition.clear();
    super.close(hasFailed);
  }

}
