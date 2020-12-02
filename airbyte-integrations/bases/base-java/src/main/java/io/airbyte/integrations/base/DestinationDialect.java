package io.airbyte.integrations.base;

import java.util.Map;

public interface DestinationDialect {

  void setContext(Map<String, DestinationWriteContext> configs);

}
