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

package io.airbyte.integrations.destination;

/**
 * When choosing identifiers names in destinations, extended Names can handle more special
 * characters than standard Names by using the quoting characters: "..."
 *
 * This class detects when such special characters are used and adds the appropriate quoting when
 * necessary.
 */
public class ExtendedNameTransformer extends StandardNameTransformer {

  @Override
  protected String convertStreamName(String input) {
    return super.convertStreamName(input);
  }

  // Temporarily disabling the behavior of the ExtendedNameTransformer, see (issue #1785)
  protected String disabled_convertStreamName(String input) {
    if (useExtendedIdentifiers(input)) {
      return "\"" + input + "\"";
    } else {
      return applyDefaultCase(input);
    }
  }

  protected String applyDefaultCase(String input) {
    return input;
  }

  protected boolean useExtendedIdentifiers(String input) {
    boolean result = false;
    if (input.matches("[^\\p{Alpha}_].*")) {
      result = true;
    } else if (input.matches(".*[^\\p{Alnum}_].*")) {
      result = true;
    }
    return result;
  }

}
