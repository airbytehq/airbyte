package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.integrations.debug.AbstractSourceDebugger;

public class PostgresDebugger extends AbstractSourceDebugger {

  @SuppressWarnings({"unchecked", "deprecation", "resource"})
  public static void main(final String[] args) throws Exception {
    final PostgresDebugger debugger = new PostgresDebugger();
    debugger.check();
    debugger.discover();
    debugger.read();
  }

  PostgresDebugger() throws Exception {
    super();
  }

  @Override
  protected PostgresSource getSource() {
    return new PostgresSource();
  }

  @Override
  protected boolean perStreamEnabled() {
    return true;
  }

  @Override
  protected JsonNode convertToDebugConfig(final JsonNode originalConfig) {
    if (!PostgresUtils.shouldFlushAfterSync(originalConfig)) {
      throw new RuntimeException("WARNING: config indicates that we are clearing the WAL log while reading data. This will mutate the WAL log"
          + " associated with the source being debugged and is not advised.");
    }
    final JsonNode debugConfig = ((ObjectNode) originalConfig.deepCopy()).put("debug_mode", true);
    return debugConfig;
  }
}