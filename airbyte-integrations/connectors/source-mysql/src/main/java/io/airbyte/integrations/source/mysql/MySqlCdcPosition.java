package io.airbyte.integrations.source.mysql;

import java.util.Objects;

public class MySqlCdcPosition {
  public final String fileName;
  public final Integer position;

  public MySqlCdcPosition(final String fileName, final Integer position) {
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
