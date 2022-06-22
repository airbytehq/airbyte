/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models.transform_models;

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
  private final AddFieldTransform addFieldTransform;
  private final RemoveFieldTransform removeFieldTransform;
  private final UpdateFieldTransform updateFieldTransform;

  public static FieldTransform createAddFieldTransform(final List<String> fieldName, final JsonNode schema) {
    return createAddFieldTransform(new AddFieldTransform(fieldName, schema));
  }

  public static FieldTransform createAddFieldTransform(final AddFieldTransform addFieldTransform) {
    return new FieldTransform(FieldTransformType.ADD_FIELD, addFieldTransform, null, null);
  }

  public static FieldTransform createRemoveFieldTransform(final List<String> fieldName, final JsonNode schema) {
    return createRemoveFieldTransform(new RemoveFieldTransform(fieldName, schema));
  }

  public static FieldTransform createRemoveFieldTransform(final RemoveFieldTransform removeFieldTransform) {
    return new FieldTransform(FieldTransformType.REMOVE_FIELD, null, removeFieldTransform, null);
  }

  public static FieldTransform createUpdateFieldTransform(final UpdateFieldTransform updateFieldTransform) {
    return new FieldTransform(FieldTransformType.UPDATE_FIELD, null, null, updateFieldTransform);
  }

  public FieldTransformType getTransformType() {
    return transformType;
  }

  public AddFieldTransform getAddFieldTransform() {
    return addFieldTransform;
  }

  public RemoveFieldTransform getRemoveFieldTransform() {
    return removeFieldTransform;
  }

  public UpdateFieldTransform getUpdateFieldTransform() {
    return updateFieldTransform;
  }

}
