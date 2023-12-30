package io.airbyte.cdk.integrations.debezium.internals.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumStateUtil;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.Properties;

public class MssqlDebeziumStateUtil implements DebeziumStateUtil {

  public JsonNode constructInitialDebeziumState(final Properties properties,
      final ConfiguredAirbyteCatalog catalog,
      final JdbcDatabase database) {
    return null; // TEMP
  }

  public static MssqlDebeziumStateAttributes getStateAttributesFromDB(final JdbcDatabase database) {
    return new MssqlDebeziumStateAttributes(); // TEMP
  }
  public record MssqlDebeziumStateAttributes() { //TODO: get attributes
  }

}
