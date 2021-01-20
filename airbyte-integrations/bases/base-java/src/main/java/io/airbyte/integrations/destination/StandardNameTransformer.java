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

import io.airbyte.commons.text.Names;
import java.time.Instant;

public class StandardNameTransformer implements NamingConventionTransformer {

  @Override
  public String getIdentifier(String name) {
    return convertStreamName(name);
  }

  @Override
  public String getRawTableName(String streamName) {
    return convertStreamName("_airbyte_raw_" + streamName);
  }

  @Override
  public String getTmpTableName(String streamName) {
    return convertStreamName("_airbyte_" + Instant.now().toEpochMilli() + "_" + streamName);
  }

  protected String convertStreamName(String input) {
    return Names.toAlphanumericAndUnderscore(input);
  }

}
