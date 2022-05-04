/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.util.Map;
import org.junit.jupiter.api.Test;

import io.airbyte.oauth.BaseOAuthFlow;

public class TikTokMarketingOAuthFlowTest extends BaseOAuthFlowTest {

  @Override
  protected BaseOAuthFlow getOAuthFlow() {
    return new TikTokMarketingOAuthFlow(getConfigRepository(), getHttpClient(), this::getConstantState);
  }

  @Override
  protected String getExpectedConsentUrl() {
    return "https://ads.tiktok.com/marketing_api/auth?app_id=app_id" +
        "&redirect_uri=https%3A%2F%2Fairbyte.io" +
        "&state=state";
  }

  @Override
  protected JsonNode getOAuthParamConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("app_id", "app_id")
        .put("secret", "secret")
        .build());
  }

  @Override
  protected List<String> getExpectedOutputPath() {
    return List.of("credentials_all");
  }

// {
//   "message": "OK",
//   "code": 0,
//   "data": {
//     "access_token": "xxxxxxxxxxxxx",
//     "scope": [
//       4
//     ],
//     "advertiser_ids": [
//       1234,
//       1234
//     ]
//   },
//   "request_id": "2020042715295501023125104093250"
// }

  @Override
  protected Map<String, String> getExpectedOutput() {
//   protected Map<String, Object> getExpectedOutput() {
    return Map.of("data", Map.of("access_token", "access_token_response"));
  }
}
