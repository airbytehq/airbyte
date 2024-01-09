package io.airbyte.integrations.source.mssql;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.source.mssql.MssqlDebeziumStateUtil.MssqlDebeziumStateAttributes;
import io.debezium.connector.sqlserver.Lsn;
import org.junit.jupiter.api.Test;

public class MssqlDebeziumStateUtilTest {

  private static String DB_NAME = "db_name";
  private static String LSN_STRING = "0000062d:00017ff0:016d";
  private static Lsn LSN = Lsn.valueOf(LSN_STRING);

  @Test
  void generateCorrectFormat() {
    MssqlDebeziumStateUtil util = new MssqlDebeziumStateUtil();
    MssqlDebeziumStateAttributes attributes = new MssqlDebeziumStateAttributes(LSN);
    JsonNode formatResult = util.format(attributes, DB_NAME);
    System.out.println(formatResult.toPrettyString());
    assertEquals("\"{\\\"commit_lsn\\\":\\\"0000062d:00017ff0:016d\\\",\\\"snapshot\\\":true,\\\"snapshot_completed\\\":true}\"", formatResult.get("[\"db_name\",{\"server\":\"db_name\",\"database\":\"db_name\"}]"));
  }
}
