/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import java.util.Objects;

public class CursorInfo {

  private final String originalCursorField;
  private final String originalCursor;
  private final long originalCursorRecordCount;

  private final String cursorField;
  private String cursor;
  private long cursorRecordCount;

  public CursorInfo(final String originalCursorField,
                    final String originalCursor,
                    final String cursorField,
                    final String cursor) {
    this(originalCursorField, originalCursor, 0L, cursorField, cursor, 0L);
  }

  public CursorInfo(final String originalCursorField,
                    final String originalCursor,
                    final long originalCursorRecordCount,
                    final String cursorField,
                    final String cursor,
                    final long cursorRecordCount) {
    this.originalCursorField = originalCursorField;
    this.originalCursor = originalCursor;
    this.originalCursorRecordCount = originalCursorRecordCount;
    this.cursorField = cursorField;
    this.cursor = cursor;
    this.cursorRecordCount = cursorRecordCount;
  }

  public String getOriginalCursorField() {
    return originalCursorField;
  }

  public String getOriginalCursor() {
    return originalCursor;
  }

  public long getOriginalCursorRecordCount() {
    return originalCursorRecordCount;
  }

  public String getCursorField() {
    return cursorField;
  }

  public String getCursor() {
    return cursor;
  }

  public long getCursorRecordCount() {
    return cursorRecordCount;
  }

  @SuppressWarnings("UnusedReturnValue")
  public CursorInfo setCursor(final String cursor) {
    this.cursor = cursor;
    return this;
  }

  public CursorInfo setCursorRecordCount(final long cursorRecordCount) {
    this.cursorRecordCount = cursorRecordCount;
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
    return Objects.equals(originalCursorField, that.originalCursorField)
        && Objects.equals(originalCursor, that.originalCursor)
        && Objects.equals(originalCursorRecordCount, that.originalCursorRecordCount)
        && Objects.equals(cursorField, that.cursorField)
        && Objects.equals(cursor, that.cursor)
        && Objects.equals(cursorRecordCount, that.cursorRecordCount);
  }

  @Override
  public int hashCode() {
    return Objects.hash(originalCursorField, originalCursor, originalCursorRecordCount, cursorField, cursor, cursorRecordCount);
  }

  @Override
  public String toString() {
    return "CursorInfo{" +
        "originalCursorField='" + originalCursorField + '\'' +
        ", originalCursor='" + originalCursor + '\'' +
        ", originalCursorRecordCount='" + originalCursorRecordCount + '\'' +
        ", cursorField='" + cursorField + '\'' +
        ", cursor='" + cursor + '\'' +
        ", cursorRecordCount='" + cursorRecordCount + '\'' +
        '}';
  }

}
