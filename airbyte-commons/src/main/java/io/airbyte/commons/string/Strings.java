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

package io.airbyte.commons.string;

import com.google.common.collect.Streams;
import java.util.stream.Collectors;
import org.apache.commons.lang3.RandomStringUtils;

public class Strings {

  public static String join(final Iterable<?> iterable, final CharSequence separator) {
    return Streams.stream(iterable)
        .map(Object::toString)
        .collect(Collectors.joining(separator));
  }

  public static String addRandomSuffix(final String base, final String separator, final int suffixLength) {
    return base + separator + RandomStringUtils.randomAlphabetic(suffixLength).toLowerCase();
  }

  public static String safeTrim(final String string) {
    return string == null ? null : string.trim();
  }

}
