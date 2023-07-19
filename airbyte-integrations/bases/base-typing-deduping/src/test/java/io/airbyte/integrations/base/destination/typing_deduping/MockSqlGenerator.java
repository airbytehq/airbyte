/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

/**
 * Basic SqlGenerator mock. See {@link TyperDeduperTest} for example usage.
 */
class MockSqlGenerator implements SqlGenerator<String> {

  @Override
  public StreamId buildStreamId(String namespace, String name, String rawNamespaceOverride) {
    return null;
  }

  @Override
  public ColumnId buildColumnId(String name) {
    return null;
  }

  @Override
  public String createTable(StreamConfig stream, String suffix) {
    return "CREATE TABLE " + stream.id().finalTableId(suffix, "");
  }

  @Override
  public String alterTable(StreamConfig stream, String existingTable) {
    return "ALTER TABLE " + stream.id().finalTableId("") + " WITH EXISTING " + existingTable;
  }

  @Override
  public String updateTable(String finalSuffix, StreamConfig stream) {
    return "UPDATE TABLE " + stream.id().finalTableId(finalSuffix, "");
  }

  @Override
  public String overwriteFinalTable(String finalSuffix, StreamId stream) {
    return "OVERWRITE TABLE " + stream.finalTableId("") + " FROM " + stream.finalTableId(finalSuffix, "");
  }

}
