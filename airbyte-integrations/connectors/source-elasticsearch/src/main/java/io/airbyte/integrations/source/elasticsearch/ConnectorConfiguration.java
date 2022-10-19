/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.elasticsearch;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Objects;

@JsonIgnoreProperties(ignoreUnknown = true)
public class ConnectorConfiguration {

  private String endpoint;
  private boolean upsert;
  private AuthenticationMethod authenticationMethod = new AuthenticationMethod();

  public ConnectorConfiguration() {}

  public static ConnectorConfiguration fromJsonNode(JsonNode config) {
    return new ObjectMapper().convertValue(config, ConnectorConfiguration.class);
  }

  public String getEndpoint() {
    return this.endpoint;
  }

  public boolean isUpsert() {
    return this.upsert;
  }

  public AuthenticationMethod getAuthenticationMethod() {
    return this.authenticationMethod;
  }

  public void setEndpoint(String endpoint) {
    this.endpoint = endpoint;
  }

  public void setUpsert(boolean upsert) {
    this.upsert = upsert;
  }

  public void setAuthenticationMethod(AuthenticationMethod authenticationMethod) {
    this.authenticationMethod = authenticationMethod;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o)
      return true;
    if (o == null || getClass() != o.getClass())
      return false;
    ConnectorConfiguration that = (ConnectorConfiguration) o;
    return upsert == that.upsert && Objects.equals(endpoint, that.endpoint) && Objects.equals(authenticationMethod, that.authenticationMethod);
  }

  @Override
  public int hashCode() {
    return Objects.hash(endpoint, upsert, authenticationMethod);
  }

  @Override
  public String toString() {
    return "ConnectorConfiguration{" +
        "endpoint='" + endpoint + '\'' +
        ", upsert=" + upsert +
        ", authenticationMethod=" + authenticationMethod +
        '}';
  }

  static class AuthenticationMethod {

    private ElasticsearchAuthenticationMethod method = ElasticsearchAuthenticationMethod.none;
    private String username;
    private String password;
    private String apiKeyId;
    private String apiKeySecret;

    public ElasticsearchAuthenticationMethod getMethod() {
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

    public void setMethod(ElasticsearchAuthenticationMethod method) {
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

    public boolean isValid() {
      return switch (this.method) {
        case none -> true;
        case basic -> Objects.nonNull(this.username) && Objects.nonNull(this.password);
        case secret -> Objects.nonNull(this.apiKeyId) && Objects.nonNull(this.apiKeySecret);
      };
    }

    @Override
    public boolean equals(Object o) {
      if (this == o)
        return true;
      if (o == null || getClass() != o.getClass())
        return false;
      AuthenticationMethod that = (AuthenticationMethod) o;
      return method == that.method &&
          Objects.equals(username, that.username) &&
          Objects.equals(password, that.password) &&
          Objects.equals(apiKeyId, that.apiKeyId) &&
          Objects.equals(apiKeySecret, that.apiKeySecret);
    }

    @Override
    public int hashCode() {
      return Objects.hash(method, username, password, apiKeyId, apiKeySecret);
    }

    @Override
    public String toString() {
      return "AuthenticationMethod{" +
          "method=" + method +
          ", username='" + username + '\'' +
          ", apiKeyId='" + apiKeyId + '\'' +
          '}';
    }

  }

}
