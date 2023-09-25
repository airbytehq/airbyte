/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.selectdb;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public class BaseResponse<T> {

  private int code;
  private String msg;
  private T data;
  private int count;

  public int getCode() {
    return code;
  }

  public String getMsg() {
    return msg;
  }

  public T getData() {
    return data;
  }

}
