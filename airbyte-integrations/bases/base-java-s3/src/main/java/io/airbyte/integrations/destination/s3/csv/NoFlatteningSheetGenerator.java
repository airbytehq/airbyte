/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.csv;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import java.util.Collections;
import java.util.List;

public class NoFlatteningSheetGenerator extends BaseSheetGenerator implements CsvSheetGenerator {

  @Override
  public List<String> getHeaderRow() {
    return Lists.newArrayList(
        JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
        JavaBaseConstants.COLUMN_NAME_DATA);
  }

  /**
   * When no flattening is needed, the record column is just one json blob.
   */
  @Override
  List<String> getRecordColumns(final JsonNode json) {
    return Collections.singletonList(Jsons.serialize(json));
  }

}
