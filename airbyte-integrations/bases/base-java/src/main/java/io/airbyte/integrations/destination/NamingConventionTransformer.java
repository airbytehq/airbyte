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
 * Destination have their own Naming conventions (which characters are valid or rejected in
 * identifiers names) This class transform a random string used to a valid identifier names for each
 * specific destination.
 */
public interface NamingConventionTransformer {

  /**
   * Handle Naming Conversions of an input name to output a valid identifier name for the desired
   * destination.
   *
   * @param name of the identifier to check proper naming conventions
   * @return modified name with invalid characters replaced by '_' and adapted for the chosen
   *         destination.
   */
  String getIdentifier(String name);

  /**
   * Same as getIdentifier but returns also the name of the table for storing raw data
   *
   * @param name of the identifier to check proper naming conventions
   * @return modified name with invalid characters replaced by '_' and adapted for the chosen
   *         destination.
   *
   * @deprecated as this is very SQL specific, prefer using getIdentifier instead
   */
  @Deprecated
  String getRawTableName(String name);

  /**
   * Same as getIdentifier but returns also the name of the table for storing tmp data
   *
   * @param name of the identifier to check proper naming conventions
   * @return modified name with invalid characters replaced by '_' and adapted for the chosen
   *         destination.
   *
   * @deprecated as this is very SQL specific, prefer using getIdentifier instead
   */
  @Deprecated
  String getTmpTableName(String name);

}
