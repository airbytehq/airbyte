/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.state;

import static java.util.Base64.getEncoder;

import java.util.*;
import java.util.stream.Collectors;
import org.bson.BsonBinary;
import org.bson.BsonBinarySubType;
import org.bson.UuidRepresentation;
import org.bson.internal.UuidHelper;
import org.bson.types.Binary;

/**
 * _id field types that are currently supported, potential types are defined <a href=
 * "https://www.mongodb.com/docs/manual/reference/operator/query/type/#std-label-document-type-available-types">here</a>
 */
public enum IdType {

  OBJECT_ID("objectId", "ObjectId"),
  STRING("string", "String"),
  INT("int", "Integer"),
  LONG("long", "Long"),
  BINARY("binData", "Binary");

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

  IdType(final String bsonType, final String javaType) {
    this.bsonType = bsonType;
    this.javaType = javaType;
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

  /**
   * Convers a collection id to a string representation for use in a saved state. Most types will be
   * converted to a string, except for Binary types which will be converted to a Base64 encoded
   * string. and UUIDs which will be converted to a human-readable string.
   *
   * @param id an _id field value
   * @param idType the type of the _id field
   * @return a string representation of the _id field
   */
  public static String idToStringRepresenation(final Object id, final IdType idType) {
    final String strId;
    if (idType == IdType.BINARY) {
      final var binLastId = (Binary) id;
      if (binLastId.getType() == BsonBinarySubType.UUID_STANDARD.getValue()) {
        strId = UuidHelper.decodeBinaryToUuid(binLastId.getData(), binLastId.getType(), UuidRepresentation.STANDARD).toString();
      } else {
        strId = getEncoder().encodeToString(binLastId.getData());
      }
    } else {
      strId = id.toString();
    }

    return strId;
  }

  /**
   * Parse a string representation of a binary _id field into a BsonBinary object. The string can be a
   * UUID or a Base64 encoded string.
   *
   * @param id a string representation of an _id field
   * @return a BsonBinary object
   */
  public static BsonBinary parseBinaryIdString(final String id) {
    try {
      return new BsonBinary(UUID.fromString(id));
    } catch (final IllegalArgumentException ex) {
      return new BsonBinary(Base64.getDecoder().decode(id));
    }
  }

}
