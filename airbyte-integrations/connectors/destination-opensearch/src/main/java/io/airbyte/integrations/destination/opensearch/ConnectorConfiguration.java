/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.opensearch;

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

    private OpenSearchAuthenticationMethod method = OpenSearchAuthenticationMethod.none;
    private String username;
    private String password;
    private String apiKeyId;
    private String apiKeySecret;

    public OpenSearchAuthenticationMethod getMethod() {
      return this.method;
    }

    public String getUsername() {
      return this.username;
    }

    public String getPassword() {
      return this.password;
    }

    public String getApiKeyId() {
      return this.apiKeyId;
    }

    public String getApiKeySecret() {
      return this.apiKeySecret;
    }

    public void setMethod(OpenSearchAuthenticationMethod method) {
      this.method = method;
    }

    public void setUsername(String username) {
      this.username = username;
    }

    public void setPassword(String password) {
      this.password = password;
    }

    public void setApiKeyId(String apiKeyId) {
      this.apiKeyId = apiKeyId;
    }

    public void setApiKeySecret(String apiKeySecret) {
      this.apiKeySecret = apiKeySecret;
    }

<<<<<<< HEAD
>>>>>>> 7edf6edbf6 (capitalize class name)
=======

>>>>>>> c01deb78a5 (fix error)
    public boolean isValid() {
      return switch (this.method) {
        case none -> true;
        case basic -> Objects.nonNull(this.username) && Objects.nonNull(this.password);
        case secret -> Objects.nonNull(this.apiKeyId) && Objects.nonNull(this.apiKeySecret);
      };
    }

  }

}
