/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.mockito.Mockito.*;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class CatalogParserTest {

  private SqlGenerator<String> sqlGenerator;
  private CatalogParser parser;

  @BeforeEach
  public void setup() {
    sqlGenerator = mock(SqlGenerator.class);
    // noop quoting logic
    when(sqlGenerator.buildColumnId(any())).thenAnswer(invocation -> {
      String fieldName = invocation.getArgument(0);
      return new ColumnId(fieldName, fieldName, fieldName);
    });
    when(sqlGenerator.buildStreamId(any(), any(), any())).thenAnswer(invocation -> {
      String namespace = invocation.getArgument(0);
      String name = invocation.getArgument(1);
      String rawNamespace = invocation.getArgument(1);
      return new StreamId(namespace, name, rawNamespace, namespace + "_abab_" + name, namespace, name);
    });

    parser = new CatalogParser(sqlGenerator);
  }

  /**
   * Both these streams will write to the same final table name ("foofoo"). Verify that they don't
   * actually use the same tablename.
   */
  @Test
  public void finalNameCollision() {
    when(sqlGenerator.buildStreamId(any(), any(), any())).thenAnswer(invocation -> {
      String originalNamespace = invocation.getArgument(0);
      String originalName = (invocation.getArgument(1));
      String originalRawNamespace = (invocation.getArgument(1));

      // emulate quoting logic that causes a name collision
      String quotedName = originalName.replaceAll("bar", "");
      return new StreamId(originalNamespace, quotedName, originalRawNamespace, originalNamespace + "_abab_" + quotedName, originalNamespace,
          originalName);
    });
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        stream("a", "foobarfoo"),
        stream("a", "foofoo")));

    final ParsedCatalog parsedCatalog = parser.parseCatalog(catalog);

    assertNotEquals(
        parsedCatalog.streams().get(0).id().finalName(),
        parsedCatalog.streams().get(1).id().finalName());
  }

  /**
   * The schema contains two fields, which will both end up named "foofoo" after quoting. Verify that
   * they don't actually use the same column name.
   */
  @Test
  public void columnNameCollision() {
    when(sqlGenerator.buildColumnId(any())).thenAnswer(invocation -> {
      String originalName = invocation.getArgument(0);

      // emulate quoting logic that causes a name collision
      String quotedName = originalName.replaceAll("bar", "");
      return new ColumnId(quotedName, originalName, quotedName);
    });
    JsonNode schema = Jsons.deserialize("""
                                        {
                                          "type": "object",
                                          "properties": {
                                            "foobarfoo": {"type": "string"},
                                            "foofoo": {"type": "string"}
                                          }
                                        }
                                        """);
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(stream("a", "a", schema)));

    final ParsedCatalog parsedCatalog = parser.parseCatalog(catalog);

    assertEquals(2, parsedCatalog.streams().get(0).columns().size());
  }

  private static ConfiguredAirbyteStream stream(String namespace, String name) {
    return stream(
        namespace,
        name,
        Jsons.deserialize("""
                          {
                            "type": "object",
                            "properties": {
                              "name": {"type": "string"}
                            }
                          }
                          """));
  }

  private static ConfiguredAirbyteStream stream(String namespace, String name, JsonNode schema) {
    return new ConfiguredAirbyteStream().withStream(
        new AirbyteStream()
            .withNamespace(namespace)
            .withName(name)
            .withJsonSchema(schema));
  }

}
