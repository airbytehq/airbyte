/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.csv;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.util.LinkedList;
import java.util.List;
import java.util.UUID;

/**
 * CSV data row = ID column + timestamp column + record columns. This class takes care of the first
 * two columns, which is shared by downstream implementations.
 */
public abstract class BaseSheetGenerator implements CsvSheetGenerator {

  public List<Object> getDataRow(final UUID id, final AirbyteRecordMessage recordMessage) {
    final List<Object> data = new LinkedList<>();
    data.add(id);
    data.add(recordMessage.getEmittedAt());
    data.addAll(getRecordColumns(recordMessage.getData()));
    return data;
  }

  @Override
  public List<Object> getDataRow(final JsonNode formattedData) {
    return new LinkedList<>(getRecordColumns(formattedData));
  }

  public List<Object> getDataRow(final UUID id, final String formattedString, final long emittedAt) {
    throw new UnsupportedOperationException("Not implemented in BaseSheetGenerator");
  }

  abstract List<String> getRecordColumns(JsonNode json);

}
