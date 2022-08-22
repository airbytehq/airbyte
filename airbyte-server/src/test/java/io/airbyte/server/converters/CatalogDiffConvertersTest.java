/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.api.model.generated.FieldTransform;
import io.airbyte.api.model.generated.StreamTransform;
import io.airbyte.commons.enums.Enums;
import io.airbyte.protocol.models.transform_models.FieldTransformType;
import io.airbyte.protocol.models.transform_models.StreamTransformType;
import org.junit.jupiter.api.Test;

class CatalogDiffConvertersTest {

  @Test
  void testEnumConversion() {
    assertTrue(Enums.isCompatible(StreamTransform.TransformTypeEnum.class, StreamTransformType.class));
    assertTrue(Enums.isCompatible(FieldTransform.TransformTypeEnum.class, FieldTransformType.class));
  }

}
