/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris;

import com.google.common.base.Preconditions;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;
import org.apache.commons.codec.binary.Base64;
import org.apache.http.HttpEntity;
import org.apache.http.HttpHeaders;
import org.apache.http.client.methods.HttpPut;
import org.apache.http.entity.StringEntity;

public class StreamLoadHttpPutBuilder {

  String url;

  Map<String, String> prop;

  HttpEntity httpEntity;

  private StreamLoadHttpPutBuilder() {
    this.prop = new HashMap<>();
  }

  public static StreamLoadHttpPutBuilder builder() {
    return new StreamLoadHttpPutBuilder();
  }

  public StreamLoadHttpPutBuilder setUrl(String url) {
    this.url = url;
    return this;
  }

  // 用户最好设置Expect Header字段内容100-continue，这样可以在某些出错场景下避免不必要的数据传输
  public StreamLoadHttpPutBuilder addCommonHeader() {
    prop.put(HttpHeaders.EXPECT, "100-continue");
    return this;
  }

  public StreamLoadHttpPutBuilder enable2PC(Boolean bool) {
    prop.put("two_phase_commit", bool.toString());
    return this;
  }

  public StreamLoadHttpPutBuilder baseAuth(String user, String password) {
    byte[] encoded = Base64.encodeBase64(user.concat(":").concat(password).getBytes(StandardCharsets.UTF_8));
    prop.put(HttpHeaders.AUTHORIZATION, "Basic " + new String(encoded, StandardCharsets.UTF_8));
    return this;
  }

  public StreamLoadHttpPutBuilder addTxnId(long txnID) {
    prop.put("txn_id", String.valueOf(txnID));
    return this;
  }

  public StreamLoadHttpPutBuilder commit() {
    prop.put("txn_operation", "commit");
    return this;
  }

  public StreamLoadHttpPutBuilder abort() {
    prop.put("txn_operation", "abort");
    return this;
  }

  public StreamLoadHttpPutBuilder setEntity(HttpEntity httpEntity) {
    this.httpEntity = httpEntity;
    return this;
  }

  public StreamLoadHttpPutBuilder setEmptyEntity() {
    try {
      this.httpEntity = new StringEntity("");
    } catch (Exception e) {
      throw new IllegalArgumentException(e);
    }
    return this;
  }

  public StreamLoadHttpPutBuilder addProperties(Properties properties) {
    properties.forEach((key, value) -> prop.put(String.valueOf(key), String.valueOf(value)));
    return this;
  }

  public StreamLoadHttpPutBuilder setLabel(String label) {
    prop.put("label", label);
    return this;
  }

  public HttpPut build() {
    Preconditions.checkNotNull(url);
    Preconditions.checkNotNull(httpEntity);
    HttpPut put = new HttpPut(url);
    prop.forEach(put::setHeader);
    put.setEntity(httpEntity);
    return put;
  }

}
