/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.selectdb.http;

import com.google.common.base.Preconditions;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import org.apache.commons.codec.binary.Base64;
import org.apache.http.HttpEntity;
import org.apache.http.HttpHeaders;
import org.apache.http.client.methods.HttpPost;

/**
 * Builder for HttpPost.
 */
public class HttpPostBuilder {

  String url;
  Map<String, String> header;
  HttpEntity httpEntity;

  public HttpPostBuilder() {
    header = new HashMap<>();
  }

  public HttpPostBuilder setUrl(String url) {
    this.url = url;
    return this;
  }

  public HttpPostBuilder baseAuth(String user, String password) {
    final String authInfo = user + ":" + password;
    byte[] encoded = Base64.encodeBase64(authInfo.getBytes(StandardCharsets.UTF_8));
    header.put(HttpHeaders.AUTHORIZATION, "Basic " + new String(encoded, StandardCharsets.UTF_8));
    return this;
  }

  public HttpPostBuilder setEntity(HttpEntity httpEntity) {
    this.httpEntity = httpEntity;
    return this;
  }

  public HttpPost build() {
    Preconditions.checkNotNull(url);
    Preconditions.checkNotNull(httpEntity);
    HttpPost put = new HttpPost(url);
    header.forEach(put::setHeader);
    put.setEntity(httpEntity);
    return put;
  }

}
