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

package io.airbyte.oauth.flows.google;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.config.persistence.ConfigRepository;
import java.io.IOException;
import java.net.http.HttpClient;
import java.util.Map;
import java.util.function.Supplier;

public class GoogleSearchConsoleOAuthFlow extends GoogleOAuthFlow {

  @VisibleForTesting
  static final String SCOPE_URL = "https://www.googleapis.com/auth/webmasters.readonly";

  public GoogleSearchConsoleOAuthFlow(ConfigRepository configRepository) {
    super(configRepository);
  }

  @VisibleForTesting
  GoogleSearchConsoleOAuthFlow(ConfigRepository configRepository, HttpClient httpClient, Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String getScope() {
    return SCOPE_URL;
  }

  @Override
  protected String getClientIdUnsafe(JsonNode config) {
    // the config object containing client ID and secret is nested inside the "authorization" object
    Preconditions.checkArgument(config.hasNonNull("authorization"));
    return super.getClientIdUnsafe(config.get("authorization"));
  }

  @Override
  protected String getClientSecretUnsafe(JsonNode config) {
    // the config object containing client ID and secret is nested inside the "authorization" object
    Preconditions.checkArgument(config.hasNonNull("authorization"));
    return super.getClientSecretUnsafe(config.get("authorization"));
  }

  @Override
  protected Map<String, Object> extractRefreshToken(JsonNode data) throws IOException {
    // the config object containing refresh token is nested inside the "authorization" object
    return Map.of("authorization", super.extractRefreshToken(data));
  }

}
