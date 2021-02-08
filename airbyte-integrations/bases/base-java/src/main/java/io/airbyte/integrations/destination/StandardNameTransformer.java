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
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class StandardNameTransformer implements NamingConventionTransformer {

  private static final int MAX_IDENTIFIER_LENGTH = 1024;

  private static final Logger LOGGER = LoggerFactory.getLogger(StandardNameTransformer.class);

  protected int getMaxIdentifierLength() {
    return MAX_IDENTIFIER_LENGTH;
  }

  @Override
  public String getIdentifier(String name) {
    if (name.length() >= getMaxIdentifierLength()) {
      final String newName = name.substring(0, getMaxIdentifierLength() - 1);
      LOGGER.warn(String.format("Identifier '%s' is too long, truncating it to: `%s`", name, newName));
      name = newName;
    }
    return Names.toAlphanumericAndUnderscore(name);
  }

}
