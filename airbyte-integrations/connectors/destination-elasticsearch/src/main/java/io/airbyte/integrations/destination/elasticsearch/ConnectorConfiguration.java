/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.elasticsearch;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Objects;
import lombok.Data;

@JsonIgnoreProperties(ignoreUnknown = true)
@Data
public class ConnectorConfiguration {

  private String endpoint;
  private boolean upsert;
  @JsonProperty("ca_certificate")
  private String caCertificate;
  private AuthenticationMethod authenticationMethod = new AuthenticationMethod();

  public static ConnectorConfiguration fromJsonNode(JsonNode config) {
    return new ObjectMapper().convertValue(config, ConnectorConfiguration.class);
  }

  @Data
  static class AuthenticationMethod {

    private ElasticsearchAuthenticationMethod method = ElasticsearchAuthenticationMethod.none;
    private String username;
    private String password;
    private String apiKeyId;
    private String apiKeySecret;

    public boolean isValid() {
      return switch (this.method) {
        case none -> true;
        case basic -> Objects.nonNull(this.username) && Objects.nonNull(this.password);
        case secret -> Objects.nonNull(this.apiKeyId) && Objects.nonNull(this.apiKeySecret);
      };
    }

  }

}
