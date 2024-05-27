/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

import static java.util.Collections.emptyList;
import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.LinkedHashMap;
import java.util.Optional;
import org.junit.jupiter.api.Test;

public class SnowflakeSqlGeneratorTest {

  private final SnowflakeSqlGenerator generator = new SnowflakeSqlGenerator(0);

  @Test
  void columnNameSpecialCharacterHandling() {
    assertAll(
        // If a ${ is present, then we should replace all of $, {, and } with underscores
        () -> assertEquals(
            new ColumnId(
                "__FOO_",
                "${foo}",
                "__FOO_"),
            generator.buildColumnId("${foo}")),
        // But normally, we should leave those characters untouched.
        () -> assertEquals(
            new ColumnId(
                "{FO$O}",
                "{fo$o}",
                "{FO$O}"),
            generator.buildColumnId("{fo$o}")));
  }

  /**
   * Similar to {@link #columnNameSpecialCharacterHandling()}, but for stream name/namespace
   */
  @Test
  void streamNameSpecialCharacterHandling() {
    assertAll(
        () -> assertEquals(
            new StreamId(
                "__FOO_",
                "__BAR_",
                "airbyte_internal",
                "__foo__raw__stream___bar_",
                "${foo}",
                "${bar}"),
            generator.buildStreamId("${foo}", "${bar}", "airbyte_internal")),
        () -> assertEquals(
            new StreamId(
                "{FO$O}",
                "{BA$R}",
                "airbyte_internal",
                "{fo$o}_raw__stream_{ba$r}",
                "{fo$o}",
                "{ba$r}"),
            generator.buildStreamId("{fo$o}", "{ba$r}", "airbyte_internal")));
  }

  @Test
  void columnCollision() {
    final CatalogParser parser = new CatalogParser(generator);
    assertEquals(
        new StreamConfig(
            new StreamId("BAR", "FOO", "airbyte_internal", "bar_raw__stream_foo", "bar", "foo"),
            DestinationSyncMode.APPEND,
            emptyList(),
            Optional.empty(),
            new LinkedHashMap<>() {

              {
                put(new ColumnId("_CURRENT_DATE", "CURRENT_DATE", "_CURRENT_DATE"), AirbyteProtocolType.STRING);
                put(new ColumnId("_CURRENT_DATE_1", "current_date", "_CURRENT_DATE_1"), AirbyteProtocolType.INTEGER);
              }

            },
            0,
            0,
            0),
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
