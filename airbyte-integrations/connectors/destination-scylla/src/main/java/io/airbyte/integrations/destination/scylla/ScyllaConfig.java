/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.scylla;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Objects;

public class ScyllaConfig {

  private final String keyspace;

  private final String username;

  private final String password;

  private final String address;

  private final int port;

  private final int replication;

  public ScyllaConfig(String keyspace, String username, String password, String address, int port, int replication) {
    this.keyspace = keyspace;
    this.username = username;
    this.password = password;
    this.address = address;
    this.port = port;
    this.replication = replication;
  }

  public ScyllaConfig(JsonNode jsonNode) {
    this.keyspace = jsonNode.get("keyspace").asText();
    this.username = jsonNode.get("username").asText();
    this.password = jsonNode.get("password").asText();
    this.address = jsonNode.get("address").asText();
    this.port = jsonNode.get("port").asInt();
    this.replication = jsonNode.get("replication").asInt(1);
  }

  public String getKeyspace() {
    return keyspace;
  }

  public String getUsername() {
    return username;
  }

  public String getPassword() {
    return password;
  }

  public String getAddress() {
    return address;
  }

  public int getPort() {
    return port;
  }

  public int getReplication() {
    return replication;
  }

  @Override
  public String toString() {
    return "ScyllaConfig{" +
        "keyspace='" + keyspace + '\'' +
        ", username='" + username + '\'' +
        ", password='" + password + '\'' +
        ", address='" + address + '\'' +
        ", port=" + port +
        ", replication=" + replication +
        '}';
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    ScyllaConfig that = (ScyllaConfig) o;
    return port == that.port && username.equals(that.username) && password.equals(that.password) &&
        address.equals(that.address);
  }

  @Override
  public int hashCode() {
    return Objects.hash(username, password, address, port);
  }

}
