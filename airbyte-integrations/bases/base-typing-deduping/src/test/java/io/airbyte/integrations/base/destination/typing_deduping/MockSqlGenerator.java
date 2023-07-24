/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

/**
 * Basic SqlGenerator mock. See {@link DefaultTyperDeduperTest} for example usage.
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
  public boolean existingSchemaMatchesStreamConfig(StreamConfig stream, String existingTable) throws TableNotMigratedException {
    return false;
  }

  @Override
  public String softReset(StreamConfig stream) {
    return "SOFT RESET " + stream.id().finalTableId("");
  }

  @Override
  public String updateTable(StreamConfig stream, String finalSuffix) {
    return "UPDATE TABLE " + stream.id().finalTableId(finalSuffix, "");
  }

  @Override
  public String overwriteFinalTable(StreamId stream, String finalSuffix) {
    return "OVERWRITE TABLE " + stream.finalTableId("") + " FROM " + stream.finalTableId(finalSuffix, "");
  }

}
