/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ArgumentsSource;

public class JsonSchemaTypeTest {

  @ParameterizedTest
  @ArgumentsSource(JsonSchemaTypeProvider.class)
  public void testFromJsonSchemaType(String type, String airbyteType, JsonSchemaType expectedJsonSchemaType) {
    assertEquals(
        expectedJsonSchemaType,
        JsonSchemaType.fromJsonSchemaType(type, airbyteType));
  }

}
