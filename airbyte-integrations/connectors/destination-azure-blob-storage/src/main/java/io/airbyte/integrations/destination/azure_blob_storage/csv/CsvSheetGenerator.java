/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.csv;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.azure_blob_storage.csv.AzureBlobStorageCsvFormatConfig.Flattening;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.util.List;
import java.util.UUID;

/**
 * This class takes case of the generation of the CSV data sheet, including the header row and the
 * data row.
 */
public interface CsvSheetGenerator {

  List<String> getHeaderRow();

  List<Object> getDataRow(UUID id, AirbyteRecordMessage recordMessage);

  final class Factory {

    public static CsvSheetGenerator create(final JsonNode jsonSchema, final AzureBlobStorageCsvFormatConfig formatConfig) {
      if (formatConfig.getFlattening() == Flattening.NO) {
        return new NoFlatteningSheetGenerator();
      } else if (formatConfig.getFlattening() == Flattening.ROOT_LEVEL) {
        return new RootLevelFlatteningSheetGenerator(jsonSchema);
      } else {
        throw new IllegalArgumentException(
            "Unexpected flattening config: " + formatConfig.getFlattening());
      }
    }

  }

}
