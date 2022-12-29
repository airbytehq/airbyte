/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.objects.serde;

import com.fasterxml.jackson.core.JacksonException;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.deser.std.StdDeserializer;
import io.airbyte.commons.protocol.objects.ConnectorSpecification;
import io.airbyte.commons.protocol.objects.impl.ConnectorSpecificationAdapter;
import java.io.IOException;

public class ConnectionSpecificationDeserializer extends StdDeserializer<ConnectorSpecification> {

  public ConnectionSpecificationDeserializer() {
    this(null);
  }

  protected ConnectionSpecificationDeserializer(Class<?> vc) {
    super(vc);
  }

  @Override
  public ConnectorSpecification deserialize(JsonParser p, DeserializationContext ctxt) throws IOException, JacksonException {
    final JsonNode node = p.getCodec().readTree(p);
    final String jsonString = node.get("object").asText();
    return ConnectorSpecificationAdapter.fromJson(jsonString);
  }

}
