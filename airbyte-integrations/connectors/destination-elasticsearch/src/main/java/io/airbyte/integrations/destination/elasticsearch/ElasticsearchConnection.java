/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import co.elastic.clients.base.RestClientTransport;
import co.elastic.clients.base.Transport;
import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._core.SearchResponse;
import co.elastic.clients.elasticsearch._core.search.Hit;
import co.elastic.clients.elasticsearch._core.search.HitsMetadata;
import co.elastic.clients.json.jackson.JacksonJsonpMapper;
import java.io.IOException;
import org.apache.http.HttpHost;
import org.elasticsearch.client.RestClient;

public class ElasticsearchConnection {

  public boolean check() throws IOException {
    // Create the low-level client
    RestClient restClient = RestClient.builder(new HttpHost("localhost", 9200)).build();

    // Create the transport that provides JSON and http services to API clients
    Transport transport = new RestClientTransport(restClient, new JacksonJsonpMapper());

    // And create our API client
    ElasticsearchClient client = new ElasticsearchClient(transport);

    // Search all items in an index that contains documents of type AppData
    SearchResponse<AppData> search = client.search(s -> s.index("test-index"), AppData.class);

    HitsMetadata<AppData> hitMeta = search.hits();
    if (hitMeta.hits().isEmpty()) {
      System.out.println("No match");
    } else {
      for (Hit<AppData> hit : hitMeta.hits()) {
        System.out.println(hit.source());
      }
    }
    return true;
  }

  public static class AppData {

    private int intValue;
    private String msg;

    public int getIntValue() {
      return intValue;
    }

    public void setIntValue(int intValue) {
      this.intValue = intValue;
    }

    public String getMsg() {
      return msg;
    }

    public void setMsg(String msg) {
      this.msg = msg;
    }

  }

}
