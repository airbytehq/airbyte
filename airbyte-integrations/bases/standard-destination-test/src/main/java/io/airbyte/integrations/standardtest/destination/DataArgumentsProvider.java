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

package io.airbyte.integrations.standardtest.destination;

import java.util.stream.Stream;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;

/**
 * Class encapsulating all arguments required for Standard Destination Tests.
 *
 * All files defined here can be found in src/main/resources of this package.
 */
public class DataArgumentsProvider implements ArgumentsProvider {

  public static final CatalogMessageTestConfigPair EXCHANGE_RATE_CONFIG =
      new CatalogMessageTestConfigPair("exchange_rate_catalog.json", "exchange_rate_messages.txt");
  public static final CatalogMessageTestConfigPair EDGE_CASE_CONFIG =
      new CatalogMessageTestConfigPair("edge_case_catalog.json", "edge_case_messages.txt");

  @Override
  public Stream<? extends Arguments> provideArguments(ExtensionContext context) {
    return Stream.of(
        Arguments.of(EXCHANGE_RATE_CONFIG.messageFile, EXCHANGE_RATE_CONFIG.catalogFile),
        Arguments.of(EDGE_CASE_CONFIG.messageFile, EDGE_CASE_CONFIG.catalogFile)
    // todo - need to use the new protocol to capture this.
    // Arguments.of("stripe_messages.txt", "stripe_schema.json")
    );

  }

  public static class CatalogMessageTestConfigPair {

    final String catalogFile;
    final String messageFile;

    public CatalogMessageTestConfigPair(String catalogFile, String messageFile) {
      this.catalogFile = catalogFile;
      this.messageFile = messageFile;
    }

  }

}
