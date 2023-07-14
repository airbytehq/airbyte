/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals.mysql;

import java.util.Objects;

public class MySqlCdcPosition {

  public final String fileName;
  public final Long position;

  public MySqlCdcPosition(final String fileName, final Long position) {
    this.fileName = fileName;
    this.position = position;
  }

  @Override
  public boolean equals(final Object obj) {
    if (obj instanceof final MySqlCdcPosition mySqlCdcPosition) {
      return fileName.equals(mySqlCdcPosition.fileName) && mySqlCdcPosition.position.equals(position);
    }
    return false;
  }

  @Override
  public int hashCode() {
    return Objects.hash(fileName, position);
  }

  @Override
  public String toString() {
    return "FileName: " + fileName + ", Position : " + position;
  }

}
