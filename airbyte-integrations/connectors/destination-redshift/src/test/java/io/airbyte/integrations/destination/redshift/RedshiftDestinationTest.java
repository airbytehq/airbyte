/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_DB_NAME;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.redshift.RedshiftDestination.DestinationType;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("RedshiftDestination")
public class RedshiftDestinationTest {

  private static final ObjectMapper mapper = MoreMappers.initMapper();

  private JsonNode buildConfigNoJdbcParameters() {
    return Jsons.jsonNode(ImmutableMap.of(
            "host", "localhost",
            "port", 1337,
            "username", "user",
            "database", "db"));
  }

  @Test
  @DisplayName("When given S3 credentials should use COPY with SUPER Datatype")
  public void useCopyStrategyTestWithSuperTmpTable() {
    final var stubConfig = mapper.createObjectNode();
    stubConfig.put("s3_bucket_name", "fake-bucket");
    stubConfig.put("s3_bucket_region", "fake-region");
    stubConfig.put("access_key_id", "test");
    stubConfig.put("secret_access_key", "test key");

    assertEquals(DestinationType.COPY_S3_WITH_SUPER_TMP_TYPE, RedshiftDestination.determineUploadMode(stubConfig));
  }

  @Test
  @DisplayName("When not given S3 credentials should use INSERT with SUPER Datatype")
  public void useInsertStrategyTestWithSuperDatatype() {
    final var stubConfig = mapper.createObjectNode();
    assertEquals(DestinationType.INSERT_WITH_SUPER_TMP_TYPE, RedshiftDestination.determineUploadMode(stubConfig));
  }

  @Test
  void testCheckIncorrectPasswordFailure() throws Exception {
    var config = buildConfigNoJdbcParameters();
    ((ObjectNode) config).put("password", "fake");
    var destination = new RedshiftDestination();
    var actual = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus(), INCORRECT_USERNAME_OR_PASSWORD.getValue());
  }

  @Test
  public void testCheckIncorrectUsernameFailure() throws Exception {
    var config = buildConfigNoJdbcParameters();
    ((ObjectNode) config).put("username", "");
    var destination = new RedshiftDestination();
    final AirbyteConnectionStatus actual = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus(), INCORRECT_USERNAME_OR_PASSWORD.getValue());
  }

  @Test
  public void testCheckIncorrectHostFailure() throws Exception {
    var config = buildConfigNoJdbcParameters();
    ((ObjectNode) config).put("host", "localhost2");
    var destination = new RedshiftDestination();
    final AirbyteConnectionStatus actual = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus(), INCORRECT_HOST_OR_PORT.getValue());
  }

  @Test
  public void testCheckIncorrectPortFailure() throws Exception {
    var config = buildConfigNoJdbcParameters();
    ((ObjectNode) config).put("port", "0000");
    var destination = new RedshiftDestination();
    final AirbyteConnectionStatus actual = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus(), INCORRECT_HOST_OR_PORT.getValue());
  }

  @Test
  public void testCheckIncorrectDataBaseFailure() throws Exception {
    var config = buildConfigNoJdbcParameters();
    ((ObjectNode) config).put("database", "wrongdatabase");
    var destination = new RedshiftDestination();
    final AirbyteConnectionStatus actual = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus(), INCORRECT_DB_NAME.getValue());
  }

}
