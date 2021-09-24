/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import io.airbyte.integrations.destination.ExtendedNameTransformer;

public class S3NameTransformer extends ExtendedNameTransformer {

  @Override
  protected String applyDefaultCase(String input) {
    return super.convertStreamName(input).toLowerCase();
  }

  @Override
  public String getIdentifier(String name) {
    return checkFirsCharInStreamName(convertStreamName(name));
  }

  private String checkFirsCharInStreamName(String name) {
    if (name.substring(0, 1).matches("[A-Za-z_]")) {
      return name;
    } else {
      return "_" + name;
    }
  }

}
