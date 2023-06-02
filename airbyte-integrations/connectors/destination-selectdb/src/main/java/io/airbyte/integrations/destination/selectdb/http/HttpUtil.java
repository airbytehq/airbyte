/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.selectdb.http;

import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.impl.client.HttpClients;

public class HttpUtil {

  private final HttpClientBuilder httpClientBuilder =
      HttpClients
          .custom()
          .disableRedirectHandling();

  public CloseableHttpClient getClient() {
    return httpClientBuilder.build();
  }

}
