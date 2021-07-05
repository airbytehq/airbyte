package io.airbyte.integrations.source.debezium.interfaces;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

@FunctionalInterface
public interface CdcConnectorMetadata {

  void addMetaData(ObjectNode event, JsonNode source);

}
