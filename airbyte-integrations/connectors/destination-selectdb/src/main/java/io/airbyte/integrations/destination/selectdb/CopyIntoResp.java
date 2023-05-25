/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.selectdb;

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.Map;

@JsonIgnoreProperties(ignoreUnknown = true)
public class CopyIntoResp extends BaseResponse {

  private String code;
  private String exception;
  private Map<String, String> result;

  public String getDataCode() {
    return code;
  }

  public String getException() {
    return exception;
  }

  public Map<String, String> getResult() {
    return result;
  }

}
