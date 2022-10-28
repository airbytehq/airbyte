/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.version;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.SerializerProvider;
import com.fasterxml.jackson.databind.ser.std.StdSerializer;
import java.io.IOException;

public class VersionSerializer extends StdSerializer<Version> {

  public VersionSerializer() {
    this(null);
  }

  public VersionSerializer(Class<Version> t) {
    super(t);
  }

  @Override
  public void serialize(Version value, JsonGenerator gen, SerializerProvider provider) throws IOException {
    gen.writeStartObject();
    gen.writeStringField("version", value.version);
    gen.writeEndObject();
  }

}
