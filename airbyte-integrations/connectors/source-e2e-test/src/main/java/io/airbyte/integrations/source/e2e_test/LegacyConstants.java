/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;

public final class LegacyConstants {

  public static final String DEFAULT_STREAM = "data";
  public static final String DEFAULT_COLUMN = "column1";
  public static final AirbyteCatalog DEFAULT_CATALOG = CatalogHelpers.createAirbyteCatalog(
      DEFAULT_STREAM,
      Field.of(DEFAULT_COLUMN, JsonSchemaPrimitive.STRING));

  private LegacyConstants() {}

}
