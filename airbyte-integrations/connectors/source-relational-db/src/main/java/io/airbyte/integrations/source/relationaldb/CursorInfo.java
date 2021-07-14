/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.source.relationaldb;

import java.util.Objects;

public class CursorInfo {

  private final String originalCursorField;
  private final String originalCursor;

  private final String cursorField;
  private String cursor;

  public CursorInfo(String originalCursorField,
                    String originalCursor,
                    String cursorField,
                    String cursor) {
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
  public CursorInfo setCursor(String cursor) {
    this.cursor = cursor;
    return this;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    CursorInfo that = (CursorInfo) o;
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
