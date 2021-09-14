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

package io.airbyte.integrations.destination.databricks;

import io.airbyte.integrations.destination.ExtendedNameTransformer;

public class DatabricksNameTransformer extends ExtendedNameTransformer {

  @Override
  public String convertStreamName(String input) {
    return applyDefaultCase(super.convertStreamName(input));
  }

  @Override
  public String getIdentifier(String name) {
    return applyDefaultCase(super.getIdentifier(name));
  }

  @Override
  public String getTmpTableName(String streamName) {
    return applyDefaultCase(super.getTmpTableName(streamName));
  }

  @Override
  public String getRawTableName(String streamName) {
    return applyDefaultCase(super.getRawTableName(streamName));
  }

  @Override
  protected String applyDefaultCase(String input) {
    return input.toLowerCase();
  }

}
