package io.airbyte.integrations.source.jdbc.iblt;

import java.io.UnsupportedEncodingException;

public class StringXORer {

  public static String xorString(final String s, final String key) {
    try {
      return new String(xor(s.getBytes("UTF-8"), key.getBytes("UTF-8")));
    } catch (final UnsupportedEncodingException e) {
      return null;
    }
  }

  private static byte[] xor(final byte[] a, final byte[] b) {
    final byte[] out = new byte[a.length];
    for (int i = 0; i < a.length; i++) {
      out[i] = (byte) (a[i] ^ b[i%b.length]);
    }
    return out;
  }
}
