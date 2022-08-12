/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.List;
import java.util.Properties;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class PostgresDebeziumStateUtilTest {

  private static final JsonNode REPLICATION_METHOD = Jsons.jsonNode(ImmutableMap.builder()
      .put("replication_slot", "replication_slot")
      .put("publication", "publication")
      .put("plugin", "pgoutput")
      .build());

  private static final JsonNode CONFIG = Jsons.jsonNode(ImmutableMap.builder()
      .put(JdbcUtils.HOST_KEY, "host")
      .put(JdbcUtils.PORT_KEY, "5432")
      .put(JdbcUtils.DATABASE_KEY, "db_jagkjrgxhw")
      .put(JdbcUtils.SCHEMAS_KEY, List.of("schema_1", "schema_2"))
      .put(JdbcUtils.USERNAME_KEY, "username")
      .put(JdbcUtils.PASSWORD_KEY, "password")
      .put(JdbcUtils.SSL_KEY, false)
      .put("replication_method", REPLICATION_METHOD)
      .build());

  // Lsn.valueOf("0/16CA330") = 23896880
  // Lsn.valueOf("0/16CA368") = 23896936
  private static final JsonNode REPLICATION_SLOT = Jsons.jsonNode(ImmutableMap.builder()
      .put("confirmed_flush_lsn", "0/16CA368")
      .put("restart_lsn", "0/16CA330")
      .build());

  private final PostgresDebeziumStateUtil postgresDebeziumStateUtil = new PostgresDebeziumStateUtil();

  @Test
  public void stateGeneratedAfterSnapshotCompletionAfterReplicationSlot() {
    final JsonNode cdcState = Jsons.deserialize(
        "{\"{\\\"schema\\\":null,\\\"payload\\\":[\\\"db_jagkjrgxhw\\\",{\\\"server\\\":\\\"db_jagkjrgxhw\\\"}]}\":\"{\\\"last_snapshot_record\\\":true,\\\"lsn\\\":23897640,\\\"txId\\\":505,\\\"ts_usec\\\":1659422332985000,\\\"snapshot\\\":true}\"}");

    final boolean savedOffsetAfterReplicationSlotLSN = postgresDebeziumStateUtil.isSavedOffsetAfterReplicationSlotLSN(new Properties(),
        new ConfiguredAirbyteCatalog(), cdcState, REPLICATION_SLOT, CONFIG);

    Assertions.assertTrue(savedOffsetAfterReplicationSlotLSN);
  }

  @Test
  public void stateGeneratedAfterSnapshotCompletionBeforeReplicationSlot() {
    final JsonNode cdcState = Jsons.deserialize(
        "{\"{\\\"schema\\\":null,\\\"payload\\\":[\\\"db_jagkjrgxhw\\\",{\\\"server\\\":\\\"db_jagkjrgxhw\\\"}]}\":\"{\\\"last_snapshot_record\\\":true,\\\"lsn\\\":23896935,\\\"txId\\\":505,\\\"ts_usec\\\":1659422332985000,\\\"snapshot\\\":true}\"}");

    final boolean savedOffsetAfterReplicationSlotLSN = postgresDebeziumStateUtil.isSavedOffsetAfterReplicationSlotLSN(new Properties(),
        new ConfiguredAirbyteCatalog(), cdcState, REPLICATION_SLOT, CONFIG);

    Assertions.assertFalse(savedOffsetAfterReplicationSlotLSN);
  }

  @Test
  public void stateGeneratedFromWalStreamingAfterReplicationSlot() {
    final JsonNode cdcState = Jsons.deserialize(
        "{\"{\\\"schema\\\":null,\\\"payload\\\":[\\\"db_jagkjrgxhw\\\",{\\\"server\\\":\\\"db_jagkjrgxhw\\\"}]}\":\"{\\\"transaction_id\\\":null,\\\"lsn_proc\\\":23901120,\\\"lsn_commit\\\":23901120,\\\"lsn\\\":23901120,\\\"txId\\\":525,\\\"ts_usec\\\":1659422649959099}\"}");

    final boolean savedOffsetAfterReplicationSlotLSN = postgresDebeziumStateUtil.isSavedOffsetAfterReplicationSlotLSN(new Properties(),
        new ConfiguredAirbyteCatalog(), cdcState, REPLICATION_SLOT, CONFIG);

    Assertions.assertTrue(savedOffsetAfterReplicationSlotLSN);
  }

  @Test
  public void stateGeneratedFromWalStreamingBeforeReplicationSlot() {
    final JsonNode cdcState = Jsons.deserialize(
        "{\"{\\\"schema\\\":null,\\\"payload\\\":[\\\"db_jagkjrgxhw\\\",{\\\"server\\\":\\\"db_jagkjrgxhw\\\"}]}\":\"{\\\"transaction_id\\\":null,\\\"lsn_proc\\\":23896935,\\\"lsn_commit\\\":23896935,\\\"lsn\\\":23896935,\\\"txId\\\":525,\\\"ts_usec\\\":1659422649959099}\"}");

    final boolean savedOffsetAfterReplicationSlotLSN = postgresDebeziumStateUtil.isSavedOffsetAfterReplicationSlotLSN(new Properties(),
        new ConfiguredAirbyteCatalog(), cdcState, REPLICATION_SLOT, CONFIG);

    Assertions.assertFalse(savedOffsetAfterReplicationSlotLSN);
  }

  @Test
  public void nullState() {
    final boolean savedOffsetAfterReplicationSlotLSN = postgresDebeziumStateUtil.isSavedOffsetAfterReplicationSlotLSN(new Properties(),
        new ConfiguredAirbyteCatalog(), null, REPLICATION_SLOT, CONFIG);

    Assertions.assertTrue(savedOffsetAfterReplicationSlotLSN);
  }

}
