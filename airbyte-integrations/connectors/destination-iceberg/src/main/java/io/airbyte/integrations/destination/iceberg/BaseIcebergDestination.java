/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.BaseConnector;
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.integrations.destination.iceberg.config.catalog.IcebergCatalogConfig;
import io.airbyte.protocol.models.Jsons;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.util.Map;
import java.util.function.Consumer;
import lombok.extern.slf4j.Slf4j;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.SparkSession.Builder;
import org.jetbrains.annotations.NotNull;

@Slf4j
public abstract class BaseIcebergDestination extends BaseConnector implements Destination {

  public BaseIcebergDestination() {}

  public abstract String getSpecJsonString() throws Exception;

  public abstract IcebergCatalogConfig getCatalogConfig(@NotNull JsonNode config);

  @NotNull
  @Override
  public ConnectorSpecification spec() throws Exception {
    return Jsons.deserialize(getSpecJsonString(), ConnectorSpecification.class);
  }

  @Override
  public AirbyteConnectionStatus check(@NotNull JsonNode config) {
    try {
      IcebergCatalogConfig icebergCatalogConfig = getCatalogConfig(config);
      icebergCatalogConfig.check();

      // getting here means Iceberg catalog check success
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      log.error("Exception attempting to access the Iceberg catalog: ", e);
      Throwable rootCause = getRootCause(e);
      String errMessage =
          "Could not connect to the Iceberg catalog with the provided configuration. \n" + e.getMessage()
              + ", root cause: " + rootCause.getClass().getSimpleName() + "(" + rootCause.getMessage() + ")";
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage(errMessage);
    }
  }

  private Throwable getRootCause(Throwable exp) {
    Throwable curCause = exp.getCause();
    if (curCause == null) {
      return exp;
    } else {
      return getRootCause(curCause);
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(@NotNull JsonNode config,
                                            @NotNull ConfiguredAirbyteCatalog catalog,
                                            @NotNull Consumer<AirbyteMessage> outputRecordCollector) {
    final IcebergCatalogConfig icebergCatalogConfig = getCatalogConfig(config);
    final Map<String, String> sparkConfMap = icebergCatalogConfig.sparkConfigMap();
    final Builder sparkBuilder = SparkSession.builder()
        .master("local")
        .appName("Airbyte->Iceberg-" + System.currentTimeMillis());
    sparkConfMap.forEach(sparkBuilder::config);
    SparkSession spark = sparkBuilder.getOrCreate();

    return new IcebergConsumer(spark, outputRecordCollector, catalog, icebergCatalogConfig);
  }

}
