/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Objects;

/*
 * Immutable configuration class for storing cassandra related config.
 */
class CassandraConfig {

  private final String keyspace;

  private final String username;

  private final String password;

  private final String address;

  private final int port;

  private final String datacenter;

  private final int replication;

  public CassandraConfig(String keyspace,
                         String username,
                         String password,
                         String address,
                         int port,
                         String datacenter,
                         int replication) {
    this.keyspace = keyspace;
    this.username = username;
    this.password = password;
    this.address = address;
    this.port = port;
    this.datacenter = datacenter;
    this.replication = replication;
  }

  public CassandraConfig(JsonNode config) {
    this.keyspace = config.get("keyspace").asText();
    this.username = config.get("username").asText();
    this.password = config.get("password").asText();
    this.address = config.get("address").asText();
    this.port = config.get("port").asInt(9042);
    this.datacenter = config.get("datacenter").asText("datacenter1");
    this.replication = config.get("replication").asInt(1);
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

  public String getDatacenter() {
    return datacenter;
  }

  public int getReplication() {
    return replication;
  }

  @Override
  public String toString() {
    return "CassandraConfig{" +
        "keyspace='" + keyspace + '\'' +
        ", username='" + username + '\'' +
        ", password='" + password + '\'' +
        ", address='" + address + '\'' +
        ", port=" + port +
        ", datacenter='" + datacenter + '\'' +
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
    CassandraConfig that = (CassandraConfig) o;
    return port == that.port && username.equals(that.username) && password.equals(that.password) &&
        address.equals(that.address) && datacenter.equals(that.datacenter);
  }

  @Override
  public int hashCode() {
    return Objects.hash(username, password, address, port, datacenter);
  }

}
