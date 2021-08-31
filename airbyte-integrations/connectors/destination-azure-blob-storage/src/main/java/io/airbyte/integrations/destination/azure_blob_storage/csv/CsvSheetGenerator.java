/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.azure_blob_storage.csv;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.azure_blob_storage.csv.AzureBlobStorageCsvFormatConfig.Flattening;
import io.airbyte.protocol.models.AirbyteRecordMessage;
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

    public static CsvSheetGenerator create(JsonNode jsonSchema, AzureBlobStorageCsvFormatConfig formatConfig) {
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
