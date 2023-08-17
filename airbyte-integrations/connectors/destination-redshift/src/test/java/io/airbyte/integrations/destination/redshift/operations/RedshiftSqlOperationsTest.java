/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.operations;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.util.Random;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("RedshiftSqlOperations")
public class RedshiftSqlOperationsTest {

  private static final Random RANDOM = new Random();

  private String generateBigString(final int addExtraCharacters) {
    final int length = RedshiftSqlOperations.REDSHIFT_VARCHAR_MAX_BYTE_SIZE + addExtraCharacters;
    return RANDOM
        .ints('a', 'z' + 1)
        .limit(length)
        .collect(StringBuilder::new, StringBuilder::appendCodePoint, StringBuilder::append)
        .toString();
  }

  @Test
  @DisplayName("isValidData should return true for valid data")
  public void isValidDataForValid() {
    JsonNode testNode = Jsons.jsonNode(ImmutableMap.builder()
        .put("id", 3)
        .put("currency", generateBigString(0))
        .put("date", "2020-10-10T00:00:00Z")
        .put("HKD", 10.5)
        .put("NZD", 1.14)
        .build());

    RedshiftSqlOperations uut = new RedshiftSqlOperations();
    boolean isValid = uut.isValidData(testNode);
    assertEquals(true, isValid);
  }
  
}
