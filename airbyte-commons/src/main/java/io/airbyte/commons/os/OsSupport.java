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

package io.airbyte.commons.os;

import com.google.common.collect.Lists;
import java.util.ArrayList;
import java.util.List;

public class OsSupport {

  /**
   * Formats the input command
   *
   * This helper is typically only necessary when calling external bash scripts.
   *
   * @param cmdParts
   * @return
   */
  public static String[] formatCmd(String... cmdParts) {
    return formatCmd(new OsUtils(), cmdParts);
  }

  public static String[] formatCmd(OsUtils osUtils, String... cmdParts) {
    if (cmdParts.length == 0){
      return cmdParts;
    }

    if (!cmdParts[0].endsWith(".sh")){
      // We need to apply windows formatting only for shell scripts since Windows doesn't support .sh files by default
      // Other commands like `docker` should work fine
      return cmdParts;
    }

    List<String> formattedParts = new ArrayList<>();
    if (osUtils.isWindows()) {
      formattedParts.addAll(Lists.newArrayList("cmd", "/c"));
    }

    formattedParts.addAll(List.of(cmdParts));

    return formattedParts.toArray(new String[] {});
  }

}
