package io.airbyte.integrations.base;

import java.util.Map;

interface CopyToDestination {

  void setContext(Map<String, DestinationCopyContext> configs);

  void execute();
}
