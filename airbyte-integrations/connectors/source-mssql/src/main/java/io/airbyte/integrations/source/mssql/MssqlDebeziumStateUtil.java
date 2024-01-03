package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumStateUtil;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.Properties;

public class MssqlDebeziumStateUtil implements DebeziumStateUtil {
  public JsonNode constructInitialDebeziumState(final Properties properties,
      final ConfiguredAirbyteCatalog catalog,
      final JdbcDatabase database) {

  }
}
