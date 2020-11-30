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

package io.airbyte.commons.enums;

import com.google.common.base.Preconditions;
import com.google.common.collect.Sets;
import java.util.Arrays;
import java.util.stream.Collectors;

public class Enums {

  public static <T1 extends Enum<T1>, T2 extends Enum<T2>> T2 convertTo(T1 ie, Class<T2> oe) {
    if (ie == null) {
      return null;
    }

    return Enum.valueOf(oe, ie.name());
  }

  public static <T1 extends Enum<T1>, T2 extends Enum<T2>> boolean isCompatible(Class<T1> c1,
                                                                                Class<T2> c2) {
    Preconditions.checkArgument(c1.isEnum());
    Preconditions.checkArgument(c2.isEnum());
    return c1.getEnumConstants().length == c2.getEnumConstants().length
        && Sets.difference(
            Arrays.stream(c1.getEnumConstants()).map(Enum::name).collect(Collectors.toSet()),
            Arrays.stream(c2.getEnumConstants()).map(Enum::name).collect(Collectors.toSet()))
            .isEmpty();
  }

}
