/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models.v0.transform_models;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.EqualsAndHashCode;
import lombok.ToString;

/**
 * Represents the diff between two fields.
 */
@AllArgsConstructor
@EqualsAndHashCode
@ToString
public final class FieldTransform {

  private final FieldTransformType transformType;
  private final List<String> fieldName;
  private final AddFieldTransform addFieldTransform;
  private final RemoveFieldTransform removeFieldTransform;
  private final UpdateFieldSchemaTransform updateFieldTransform;
  private final boolean breaking;

  public static FieldTransform createAddFieldTransform(final List<String> fieldName, final JsonNode schema) {
    return createAddFieldTransform(fieldName, new AddFieldTransform(schema));
  }

  public static FieldTransform createAddFieldTransform(final List<String> fieldName, final AddFieldTransform addFieldTransform) {
    return new FieldTransform(FieldTransformType.ADD_FIELD, fieldName, addFieldTransform, null, null, false);
  }

  public static FieldTransform createRemoveFieldTransform(final List<String> fieldName, final JsonNode schema, final Boolean breaking) {
    return createRemoveFieldTransform(fieldName, new RemoveFieldTransform(fieldName, schema), breaking);
  }

  public static FieldTransform createRemoveFieldTransform(final List<String> fieldName,
                                                          final RemoveFieldTransform removeFieldTransform,
                                                          final Boolean breaking) {
    return new FieldTransform(FieldTransformType.REMOVE_FIELD, fieldName, null, removeFieldTransform, null, breaking);
  }

  public static FieldTransform createUpdateFieldTransform(final List<String> fieldName, final UpdateFieldSchemaTransform updateFieldTransform) {
    return new FieldTransform(FieldTransformType.UPDATE_FIELD_SCHEMA, fieldName, null, null, updateFieldTransform, false);
  }

  public FieldTransformType getTransformType() {
    return transformType;
  }

  public List<String> getFieldName() {
    return fieldName;
  }

  public AddFieldTransform getAddFieldTransform() {
    return addFieldTransform;
  }

  public RemoveFieldTransform getRemoveFieldTransform() {
    return removeFieldTransform;
  }

  public UpdateFieldSchemaTransform getUpdateFieldTransform() {
    return updateFieldTransform;
  }

  public boolean breaking() {
    return breaking;
  }

}
