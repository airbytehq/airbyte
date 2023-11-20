package io.airbyte.cdk.protocol.deser;

public class StringIterator {
  private final String data;
  private int index;

  public StringIterator(final String data) {
    this.data = data;
    this.index = 0;
  }

  public char next() {
    final char ch = peek();
    index++;
    return ch;
  }

  public char peek() {
    if (!hasNext()) {
      throw new RuntimeException("Unexpected end of string");
    }
    return data.charAt(index);
  }

  public boolean hasNext() {
    return index < data.length();
  }

  public int getIndex() {
    return index;
  }

  public String substring(final int start, final int end) {
    return data.substring(start, end);
  }
}
