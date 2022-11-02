/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.version;

import com.fasterxml.jackson.core.JacksonException;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.deser.std.StdDeserializer;
import java.io.IOException;

public class VersionDeserializer extends StdDeserializer<Version> {

  public VersionDeserializer() {
    this(null);
  }

  public VersionDeserializer(Class<?> vc) {
    super(vc);
  }

  @Override
  public Version deserialize(JsonParser p, DeserializationContext ctxt) throws IOException, JacksonException {
    final JsonNode node = p.getCodec().readTree(p);
    final String v = node.get("version").asText();
    return new Version(v);
  }

}
