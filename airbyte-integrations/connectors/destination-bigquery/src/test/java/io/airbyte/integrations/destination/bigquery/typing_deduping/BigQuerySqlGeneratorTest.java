/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static java.util.Collections.emptyList;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.google.cloud.bigquery.Clustering;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.TimePartitioning;
import com.google.common.collect.ImmutableList;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.Union;
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class BigQuerySqlGeneratorTest {

  private final BigQuerySqlGenerator generator = new BigQuerySqlGenerator("foo", "US");

  @Test
  public void testBuildColumnId() {
    // Uninteresting names are unchanged
    assertEquals(
        new ColumnId("foo", "foo", "foo"),
        generator.buildColumnId("foo"));
  }
  @Test
  void columnCollision() {
    final CatalogParser parser = new CatalogParser(generator);
    assertEquals(
        new StreamConfig(
            new StreamId("bar", "foo", "airbyte_internal", "bar_raw__stream_foo", "bar", "foo"),
            SyncMode.INCREMENTAL,
            DestinationSyncMode.APPEND,
            emptyList(),
            Optional.empty(),
            new LinkedHashMap<>() {

              {
                put(new ColumnId("CURRENT_DATE", "CURRENT_DATE", "current_date"), AirbyteProtocolType.STRING);
                put(new ColumnId("current_date_1", "current_date", "current_date_1"), AirbyteProtocolType.INTEGER);
              }

            }),
        parser.toStreamConfig(new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(new AirbyteStream()
                .withName("foo")
                .withNamespace("bar")
                .withJsonSchema(Jsons.deserialize(
                    """
                    {
                      "type": "object",
                      "properties": {
                        "CURRENT_DATE": {"type": "string"},
                        "current_date": {"type": "integer"}
                      }
                    }
                    """)))));
  }

}
