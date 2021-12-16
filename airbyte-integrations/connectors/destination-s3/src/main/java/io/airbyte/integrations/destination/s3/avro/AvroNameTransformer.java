/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

import io.airbyte.integrations.destination.ExtendedNameTransformer;

import java.util.Arrays;
import java.util.stream.Collectors;

public class AvroNameTransformer extends ExtendedNameTransformer {

  @Override
  protected String applyDefaultCase(final String input) {
    return super.convertStreamName(input).toLowerCase();
  }

  @Override
  public String getIdentifier(final String name) {
    return checkFirsCharInStreamName(convertStreamName(name));
  }

  private String checkFirsCharInStreamName(final String name) {
    if (name.substring(0, 1).matches("[A-Za-z_]")) {
      return name;
    } else {
      return "_" + name;
    }
  }

  public static String resolveNamespace(String fullPathToNode) {
    return fullPathToNode==null ? null : Arrays.stream(fullPathToNode.split("/"))
            .filter(key -> !key.isBlank())
            .filter(key -> !key.equals("items"))
            .filter(key -> !key.equals("properties"))
            .filter(key -> !key.equals("format"))
            .collect(Collectors.joining("."));
  }

}
