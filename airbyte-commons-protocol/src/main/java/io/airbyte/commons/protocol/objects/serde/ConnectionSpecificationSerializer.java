/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.objects.serde;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.SerializerProvider;
import com.fasterxml.jackson.databind.ser.std.StdSerializer;
import io.airbyte.commons.protocol.objects.ConnectorSpecification;
import java.io.IOException;

public class ConnectionSpecificationSerializer extends StdSerializer<ConnectorSpecification> {

  public ConnectionSpecificationSerializer() {
    this(null);
  }

  protected ConnectionSpecificationSerializer(Class<ConnectorSpecification> t) {
    super(t);
  }

  @Override
  public void serialize(ConnectorSpecification value, JsonGenerator gen, SerializerProvider provider) throws IOException {
    gen.writeStartObject();
    gen.writeStringField("object", value.toJson());
    gen.writeEndObject();
  }

}
