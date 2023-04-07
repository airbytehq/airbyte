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
import org.apache.http.client.methods.HttpPut;
import org.apache.http.entity.StringEntity;

public class HttpPutBuilder {

  String url;
  Map<String, String> header;
  HttpEntity httpEntity;

  public HttpPutBuilder() {
    header = new HashMap<>();
  }

  public HttpPutBuilder setUrl(String url) {
    this.url = url;
    return this;
  }

  public HttpPutBuilder setFileName(String fileName) {
    header.put("fileName", fileName);
    return this;
  }

  public HttpPutBuilder setEmptyEntity() {
    try {
      this.httpEntity = new StringEntity("");
    } catch (Exception e) {
      throw new IllegalArgumentException(e);
    }
    return this;
  }

  public HttpPutBuilder setCommonHeader() {
    header.put(HttpHeaders.EXPECT, "100-continue");
    return this;
  }

  public HttpPutBuilder baseAuth(String user, String password) {
    final String authInfo = user + ":" + password;
    byte[] encoded = Base64.encodeBase64(authInfo.getBytes(StandardCharsets.UTF_8));
    header.put(HttpHeaders.AUTHORIZATION, "Basic " + new String(encoded, StandardCharsets.UTF_8));
    return this;
  }

  public HttpPutBuilder setEntity(HttpEntity httpEntity) {
    this.httpEntity = httpEntity;
    return this;
  }

  public HttpPut build() {
    Preconditions.checkNotNull(url);
    Preconditions.checkNotNull(httpEntity);
    HttpPut put = new HttpPut(url);
    header.forEach(put::setHeader);
    put.setEntity(httpEntity);
    return put;
  }

}
