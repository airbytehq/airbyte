/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.state;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.bson.types.ObjectId;

/**
 * _id field types that are currently supported, potential types are defined <a href=
 * "https://www.mongodb.com/docs/manual/reference/operator/query/type/#std-label-document-type-available-types">here</a>
 */
public enum IdType {

  OBJECT_ID("objectId", "ObjectId", ObjectId::new),
  STRING("string", "String", s -> s),
  INT("int", "Integer", Integer::valueOf),
  LONG("long", "Long", Long::valueOf);

  private static final Map<String, IdType> byBsonType = new HashMap<>();
  static {
    for (final var idType : IdType.values()) {
      byBsonType.put(idType.bsonType.toLowerCase(), idType);
    }
  }

  private static final Map<String, IdType> byJavaType = new HashMap<>();
  static {
    for (final var idType : IdType.values()) {
      byJavaType.put(idType.javaType.toLowerCase(), idType);
    }
  }

  /** A comma-separated, human-readable list of supported _id types. */
  public static final String SUPPORTED;
  static {
    SUPPORTED = Arrays.stream(IdType.values())
        .map(e -> e.bsonType)
        .collect(Collectors.joining(", "));
  }

  /** MongoDb BSON type */
  private final String bsonType;
  /** Java class name type */
  private final String javaType;
  /** Converter for converting a string value into an appropriate MongoDb type. */
  private final Function<String, Object> converter;

  IdType(final String bsonType, final String javaType, final Function<String, Object> converter) {
    this.bsonType = bsonType;
    this.javaType = javaType;
    this.converter = converter;
  }

  public Object convert(final String t) {
    return converter.apply(t);
  }

  public static Optional<IdType> findByBsonType(final String bsonType) {
    if (bsonType == null) {
      return Optional.empty();
    }
    return Optional.ofNullable(byBsonType.get(bsonType.toLowerCase()));
  }

  public static Optional<IdType> findByJavaType(final String javaType) {
    if (javaType == null) {
      return Optional.empty();
    }
    return Optional.ofNullable(byJavaType.get(javaType.toLowerCase()));
  }

}
