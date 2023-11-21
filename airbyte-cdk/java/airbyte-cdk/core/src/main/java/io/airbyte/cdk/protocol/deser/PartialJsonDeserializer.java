/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.protocol.deser;

import io.airbyte.commons.json.Jsons;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Supplier;

public class PartialJsonDeserializer {

  /**
   * Given a StringIterator over a serialized JSON object, advance the iterator through the object.
   * Any time we find an object key matching one of the consumers, we position the iterator at the
   * start of the value for that key and call the consumer. The consumer should read from the same
   * iterator that is passed into this method.
   * <p>
   * The consumers MUST fully read the value (including any nested objects), and MUST NOT read any
   * non-whitespace characters after the value (they MAY read whitespace, but aren't required to).
   * <p>
   * We intentionally define the consumers as accepting an iterator instead of the substring to avoid
   * duplicating the data in-memory when possible. Consumers may need to extract the substring, but
   * this method is designed to operate solely on the original copy of the string, even in recursive
   * calls.
   *
   * @param constructor A function that returns a new instance of the object to be deserialized into.
   * @param keyValueConsumers The consumers to handle each field of the object
   * @param exitParseEarly Whether to stop parsing the object after all consumers have been called.
   *        Top-level calls probably should set this to true, but recursive calls (i.e. calls within
   *        the keyValueConsumers) MUST set this to false.
   *
   * @return The object, or null if the input string is "null".
   */
  public static <T> T parseObject(final StringIterator data,
                                  final Supplier<T> constructor,
                                  final Map<String, Consumer<T>> keyValueConsumers,
                                  final boolean exitParseEarly) {
    return parseObject(data, constructor, new MapParseHandler<>(keyValueConsumers), exitParseEarly);
  }

  /**
   * Extract the serialized values for a set of keys from a JSON object.
   */
  public static Map<String, String> parseObject(final StringIterator data, final Collection<String> keysToExtract) {
    final Map<String, Consumer<Map<String, String>>> consumers = new HashMap<>();
    for (final String key : keysToExtract) {
      consumers.put(key, output -> output.put(key, PartialJsonDeserializer.readSerializedValue(data)));
    }
    return parseObject(data, HashMap::new, consumers, true);
  }

  /**
   * Extract all serialized values from a JSON object.
   */
  public static Map<String, String> parseObject(final StringIterator data) {
    return parseObject(
        data,
        HashMap::new,
        key -> output -> output.put(key, PartialJsonDeserializer.readSerializedValue(data))
    );
  }

  /**
   * Perform some processing on each key/value pair in a JSON object. This method is only useful if
   * you don't already know all the keys that can be present in the object AND you need to handle all
   * of the keys. If you know all the keys, you should use {@link #parseObject(StringIterator, Supplier, Map, boolean)}
   * instead.
   */
  public static <T> T parseObject(final StringIterator data,
                                  final Supplier<T> constructor,
                                  final Function<String, Consumer<T>> keyValueConsumers) {
    return parseObject(data, constructor, new FunctionParseHandler<>(keyValueConsumers), false);
  }

  interface ParseHandler<T> {
    Consumer<T> getConsumer(String key);
    boolean isDone();
  }

  private record MapParseHandler<T>(Map<String, Consumer<T>> consumers) implements ParseHandler<T> {
    @Override
    public Consumer<T> getConsumer(final String key) {
      return consumers.remove(key);
    }

    @Override
    public boolean isDone() {
      return consumers.isEmpty();
    }
  }

  private record FunctionParseHandler<T>(Function<String, Consumer<T>> consumerFunction) implements ParseHandler<T> {
    @Override
    public Consumer<T> getConsumer(final String key) {
      return consumerFunction.apply(key);
    }

    @Override
    public boolean isDone() {
      return false;
    }
  }

  private static <T> T parseObject(final StringIterator data,
                                  final Supplier<T> constructor,
                                  final ParseHandler<T> parseHandler,
                                  final boolean exitParseEarly) {
    skipWhitespace(data);
    final char firstChar = data.peek();
    if (firstChar == 'n') {
      skipExactString(data, "null");
      return null;
    }

    skipWhitespaceAndCharacter(data, '{');
    skipWhitespace(data);

    final T object = constructor.get();

    // handle empty object specially
    if (data.peek() == '}') {
      data.next();
      return object;
    }
    while (data.hasNext()) {
      // Read a key/value pair
      final String key = readStringValue(data);
      skipWhitespaceAndCharacter(data, ':');
      skipWhitespace(data);
      // Pass to the appropriate consumer, or read past the value
      final Consumer<T> consumer = parseHandler.getConsumer(key);
      if (consumer != null) {
        consumer.accept(object);
        if (exitParseEarly && parseHandler.isDone()) {
          return object;
        }
      } else {
        skipValue(data);
      }

      // Check if we have another entry in the object
      skipWhitespace(data);
      final char ch = data.next();
      if (ch == '}') {
        return object;
      } else if (ch != ',') {
        throw new RuntimeException("Unexpected '" + ch + "'" + " at index " + data.getIndex() + "; expected '}' or ','.");
      }
    }
    throw new RuntimeException("Unexpected end of string");
  }

  /**
   * Read a JSON value from the iterator and return it as a serialized string.
   */
  public static String readSerializedValue(final StringIterator data) {
    skipWhitespace(data);
    final int start = data.getIndex();
    skipValue(data);
    final int end = data.getIndex();
    // TODO maybe faster if we fill a stringbuilder while we're reading the value, rather than skipping
    // the value?
    return data.substring(start, end);
  }

  /**
   * Read a JSON string into a Java string. Un-escapes characters and strips the surrounding quotes.
   * Assumes the iterator is pointing at the opening quote.
   */
  public static String readStringValue(final StringIterator data) {
    // TODO this is heavily copied from skipValue's string-handling branch, can we unify them?
    skipWhitespaceAndCharacter(data, '"');
    final StringBuilder sb = new StringBuilder();
    while (data.hasNext()) {
      final char ch = data.next();
      switch (ch) {
        case '"' -> {
          return sb.toString();
        }
        case '\\' -> {
          final char escapeChar = data.next();
          switch (escapeChar) {
            // Basic escape characters
            case '"' -> sb.append('"');
            case '\\' -> sb.append('\\');
            case '/' -> sb.append('/');
            case 'b' -> sb.append('\b');
            case 'f' -> sb.append('\f');
            case 'n' -> sb.append('\n');
            case 'r' -> sb.append('\r');
            case 't' -> sb.append('\t');
            // Unicode escape (e.g. "\uf00d")
            case 'u' -> {
              String hexString = "";
              for (int i = 0; i < 4; i++) {
                hexString += data.next();
              }
              // TODO is this correct?
              final int value = Integer.parseInt(hexString, 16);
              sb.append((char) value);
            }
            // Invalid escape
            default -> throw new RuntimeException("Invalid escape character '" + escapeChar + "'" + " at index " + data.getIndex());
          }
        }
        default -> sb.append(ch);
      }
    }
    throw new RuntimeException("Unexpected end of string");
  }

  // TODO split this into readLong, readDouble, readBigInteger, readBigNumber
  public static Number readNumber(final StringIterator data) {
    final char firstChar = data.peek();
    if (firstChar == 'n') {
      skipExactString(data, "null");
      return null;
    }

    final int startIndex = data.getIndex();
    skipNumber(data);
    final String numberStr = data.substring(startIndex, data.getIndex());
    if (numberStr.contains(".")) {
      return Double.parseDouble(numberStr);
    } else {
      // TODO handle integer exponent syntax, e.g. parse 1e6 into 1000000
      return Long.parseLong(numberStr);
    }
  }

  public static <T> List<T> readList(final StringIterator data, final Function<StringIterator, T> valueMapper) {
    // Check the first character. Either it's a null, or it's an opening bracket.
    final char firstChar = data.next();
    if (firstChar == 'n') {
      skipExactString(data, "ull");
      return null;
    }
    if (firstChar != '[') {
      throw new IllegalStateException("Unexpected '" + firstChar + "'" + " at index " + data.getIndex());
    }

    final List<T> list = new ArrayList<>();

    skipWhitespace(data);
    // Check for empty array
    if (data.peek() == ']') {
      data.next();
      return list;
    }
    // Loop over the array
    while (data.hasNext()) {
      list.add(valueMapper.apply(data));
      skipWhitespace(data);
      final char ch = data.next();
      if (ch == ']') {
        return list;
      } else if (ch != ',') {
        throw new RuntimeException("Unexpected '" + ch + "'" + " at index " + data.getIndex() + "; expected ']' or ','.");
      }
    }

    throw new IllegalStateException("Unexpected end of input while processing list");
  }

  private static void skipValue(final StringIterator data) {
    skipWhitespace(data);
    final char firstChar = data.peek();
    switch (firstChar) {
      case '"' -> {
        // Skip the opening quote and start reading the string
        data.next();
        while (data.hasNext()) {
          final char ch = data.next();
          if (ch == '"') {
            return;
          } else if (ch == '\\') {
            final char escapeChar = data.next();
            switch (escapeChar) {
              // Basic escape characters
              case '"', '\\', '/', 'b', 'f', 'n', 'r', 't' -> {
                // do nothing, this is just part of the string literal
              }
              // Unicode escape (e.g. "\uf00d")
              case 'u' -> {
                for (int i = 0; i < 4; i++) {
                  final char expectedHexDigit = data.next();
                  final boolean isDigit = '0' <= expectedHexDigit && expectedHexDigit <= '9';
                  final boolean isLowercaseHexDigit = 'a' <= expectedHexDigit && expectedHexDigit <= 'f';
                  final boolean isUppercaseHexDigit = 'A' <= expectedHexDigit && expectedHexDigit <= 'F';
                  if (!isDigit && !isLowercaseHexDigit && !isUppercaseHexDigit) {
                    throw new RuntimeException("Expected hex digit but got '" + expectedHexDigit + "'" + " at index " + data.getIndex());
                  }
                }
              }
              // Invalid escape
              default -> throw new RuntimeException("Invalid escape character '" + escapeChar + "'" + " at index " + data.getIndex());
            }
          }
        }
        throw new RuntimeException("Unexpected end of string");
      }
      case '{' -> {
        // Skip the opening curly brace and start reading the object
        data.next();
        skipWhitespace(data);
        // handle empty object
        if (data.peek() == '}') {
          data.next();
          return;
        }
        // Otherwise, read a key/value pair
        if (data.peek() != '"') {
          // Keys must be strings.
          throw new RuntimeException("Expected '\"' at index " + data.getIndex() + " but got '" + data.peek() + "'");
        }
        skipValue(data);
        skipWhitespaceAndCharacter(data, ':');
        skipWhitespace(data);
        skipValue(data);
        // and then read the rest of the object
        readToEndOfObject(data);
      }
      case '[' -> {
        // Skip the opening bracket and start reading the object
        data.next();
        skipWhitespace(data);
        // Check for empty array
        if (data.peek() == ']') {
          data.next();
          return;
        }
        // Loop over the array
        while (data.hasNext()) {
          skipValue(data);
          skipWhitespace(data);
          final char ch = data.next();
          if (ch == ']') {
            return;
          } else if (ch != ',') {
            throw new RuntimeException("Unexpected '" + ch + "'" + " at index " + data.getIndex() + "; expected ']' or ','.");
          }
        }
      }
      case '-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' -> skipNumber(data);
      case 't' -> skipExactString(data, "true");
      case 'f' -> skipExactString(data, "false");
      case 'n' -> skipExactString(data, "null");
      default -> throw new RuntimeException("Unexpected character '" + firstChar + "'" + " at index " + data.getIndex());
    }
  }

  private static void skipNumber(final StringIterator data) {
    // check for negative number
    final char firstChar = data.peek();
    if (firstChar == '-') {
      data.next();
    }

    // Skip the integer part of the number
    skipDigits(data);

    // Skip the fractional part of the number
    char next = data.peek();
    if (next == '.') {
      data.next();
      skipDigits(data);
    }

    // Skip the exponent
    next = data.peek();
    if (next == 'e' || next == 'E') {
      data.next();
      next = data.peek();
      if (next == '+' || next == '-') {
        data.next();
      }
      skipDigits(data);
    }
  }

  /**
   * Advance the iterator past the next closing curly brace, ignoring all key/value pairs. Assumes
   * that the iterator is pointing inside an object, immediately after a key/value pair. Throw an
   * exception if we reach the end of the string before finding a closing brace, or if we find a
   * different unexpected terminator (e.g. a closing square bracket).
   */
  private static void readToEndOfObject(final StringIterator data) {
    while (data.hasNext()) {
      skipWhitespace(data);
      final char ch = data.next();
      if (ch == '}') {
        return;
      } else if (ch == ',') {
        // advance past the next key/value pair
        skipValue(data);
        skipWhitespaceAndCharacter(data, ':');
        skipValue(data);
      } else {
        throw new RuntimeException("Unexpected '" + ch + "'" + " at index " + data.getIndex() + ". Expected '}' or ','.");
      }
    }
    throw new RuntimeException("Unexpected end of string");
  }

  private static void skipWhitespace(final StringIterator data) {
    while (data.hasNext()) {
      final char ch = data.peek();
      if (!Character.isWhitespace(ch)) {
        return;
      }
      data.next();
    }
  }

  private static void skipWhitespaceAndCharacter(final StringIterator data, final char ch) {
    skipWhitespace(data);
    final char actualCharacter = data.peek();
    if (actualCharacter == ch) {
      data.next();
    } else {
      throw new RuntimeException("Expected '" + ch + "'" + " at index " + data.getIndex() + " but got '" + actualCharacter + "'");
    }
  }

  private static void skipExactString(final StringIterator data, final String str) {
    for (int i = 0; i < str.length(); i++) {
      final char target = str.charAt(i);
      final char actualChar = data.next();
      if (actualChar != target) {
        throw new RuntimeException("Expected '" + target + "'" + " at index " + data.getIndex() + " but got '" + actualChar + "'");
      }
    }
  }

  /**
   * Skip characters until we find a non-numeric character
   */
  private static void skipDigits(final StringIterator data) {
    while (data.hasNext()) {
      final char ch = data.peek();
      if (ch < '0' || '9' < ch) {
        return;
      }
      data.next();
    }
  }

}
