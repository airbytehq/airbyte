package io.airbyte.db.mongodb;

import io.airbyte.protocol.models.JsonSchemaPrimitive;
import org.jooq.DataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongoUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoUtils.class);

  public static JsonSchemaPrimitive getType(DataType dataType) {
    return JsonSchemaPrimitive.STRING;
  }

}
