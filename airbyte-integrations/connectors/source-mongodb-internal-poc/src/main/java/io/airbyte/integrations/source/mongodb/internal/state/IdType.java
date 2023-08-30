/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.state;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.bson.types.ObjectId;

/**
 * _id field types that are currently supported, potential types are defined
 * <a href="https://www.mongodb.com/docs/manual/reference/operator/query/type/#std-label-document-type-available-types">here</a>
 */
public enum IdType {
  OBJECT_ID("objectId", ObjectId::new),
  STRING("string", s -> s),
  INT("int", Integer::valueOf),
  LONG("long", Long::valueOf);

  private static final Map<String, IdType> byMongoDbType = new HashMap<>();
  static {
    for (final var idType : IdType.values()) {
      byMongoDbType.put(idType.mongoDbType, idType);
    }
  }

  /** A comma-separated, human-readable list of supported _id types. */
  public static final String SUPPORTED;
  static {
    SUPPORTED = Arrays.stream(IdType.values())
        .map(e -> e.mongoDbType)
        .collect(Collectors.joining(", "));
  }

  /** Mongodb BSON type */
  private final String mongoDbType;
  /** Converter for converting a string value into an appropriate MongoDb type. */
  private final Function<String, Object> converter;
  IdType(final String mongoDbType, final Function<String, Object> converter) {
    this.mongoDbType = mongoDbType;
    this.converter = converter;
  }

  public Object convert(final String t) {
    return converter.apply(t);
  }

  public static Optional<IdType> findByMongoDbType(final String mongoDbType) {
    return Optional.ofNullable(byMongoDbType.get(mongoDbType));
  }
}
