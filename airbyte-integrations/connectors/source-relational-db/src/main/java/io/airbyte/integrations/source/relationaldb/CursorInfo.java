/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import java.util.Objects;

public class CursorInfo {

  private final String originalCursorField;
  private final String originalCursor;

  private final String cursorField;
  private String cursor;

  public CursorInfo(final String originalCursorField,
                    final String originalCursor,
                    final String cursorField,
                    final String cursor) {
    this.originalCursorField = originalCursorField;
    this.originalCursor = originalCursor;
    this.cursorField = cursorField;
    this.cursor = cursor;
  }

  public String getOriginalCursorField() {
    return originalCursorField;
  }

  public String getOriginalCursor() {
    return originalCursor;
  }

  public String getCursorField() {
    return cursorField;
  }

  public String getCursor() {
    return cursor;
  }

  @SuppressWarnings("UnusedReturnValue")
  public CursorInfo setCursor(final String cursor) {
    this.cursor = cursor;
    return this;
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final CursorInfo that = (CursorInfo) o;
    return Objects.equals(originalCursorField, that.originalCursorField) && Objects
        .equals(originalCursor, that.originalCursor)
        && Objects.equals(cursorField, that.cursorField) && Objects.equals(cursor, that.cursor);
  }

  @Override
  public int hashCode() {
    return Objects.hash(originalCursorField, originalCursor, cursorField, cursor);
  }

  @Override
  public String toString() {
    return "CursorInfo{" +
        "originalCursorField='" + originalCursorField + '\'' +
        ", originalCursor='" + originalCursor + '\'' +
        ", cursorField='" + cursorField + '\'' +
        ", cursor='" + cursor + '\'' +
        '}';
  }

}
