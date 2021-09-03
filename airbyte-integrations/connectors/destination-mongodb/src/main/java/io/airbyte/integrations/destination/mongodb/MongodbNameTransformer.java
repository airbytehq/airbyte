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

package io.airbyte.integrations.destination.mongodb;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.integrations.destination.ExtendedNameTransformer;

@VisibleForTesting
public class MongodbNameTransformer extends ExtendedNameTransformer {

  @Override
  protected String applyDefaultCase(String input) {
    return input.toLowerCase();
  }

  @Override
  public String convertStreamName(String input) {
    String result = super.convertStreamName(input);
    if (!result.isEmpty() && result.charAt(0) == '_') {
      result = result.substring(1);
    }
    return maxStringLength(result, 64);
  }

  /* Helpers */

  private String maxStringLength(String value, Integer length) {
    if (value.length() <= length) {
      return value;
    }
    return value.substring(0, length);
  }

}
