/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import io.airbyte.api.model.generated.FieldNameAndSchema;
import io.airbyte.api.model.generated.FieldSchemaUpdate;
import io.airbyte.api.model.generated.FieldTransform;
import io.airbyte.api.model.generated.StreamDescriptor;
import io.airbyte.api.model.generated.StreamTransform;
import io.airbyte.commons.enums.Enums;
import io.airbyte.protocol.models.transform_models.FieldTransformType;
import io.airbyte.protocol.models.transform_models.StreamTransformType;
import java.util.List;
import java.util.Optional;

/**
 * Utility methods for converting between internal and API representation of catalog diffs.
 */
public class CatalogDiffConverters {

  public static StreamTransform streamTransformToApi(final io.airbyte.protocol.models.transform_models.StreamTransform transform) {
    return new StreamTransform()
        .transformType(Enums.convertTo(transform.getTransformType(), StreamTransform.TransformTypeEnum.class))
        .addStream(addStreamToApi(transform).orElse(null))
        .removeStream(removeStreamToApi(transform).orElse(null))
        .updateStream(updateStreamToApi(transform).orElse(null));
  }

  public static Optional<StreamDescriptor> addStreamToApi(final io.airbyte.protocol.models.transform_models.StreamTransform transform) {
    if (transform.getTransformType() == StreamTransformType.ADD_STREAM) {
      return Optional.ofNullable(ProtocolConverters.streamDescriptorToApi(transform.getAddStreamTransform().getStreamDescriptor()));
    } else {
      return Optional.empty();
    }
  }

  public static Optional<StreamDescriptor> removeStreamToApi(final io.airbyte.protocol.models.transform_models.StreamTransform transform) {
    if (transform.getTransformType() == StreamTransformType.REMOVE_STREAM) {
      return Optional.ofNullable(ProtocolConverters.streamDescriptorToApi(transform.getRemoveStreamTransform().getStreamDescriptor()));
    } else {
      return Optional.empty();
    }
  }

  public static Optional<List<FieldTransform>> updateStreamToApi(final io.airbyte.protocol.models.transform_models.StreamTransform transform) {
    if (transform.getTransformType() == StreamTransformType.UPDATE_STREAM) {
      return Optional.ofNullable(transform.getUpdateStreamTransform()
          .getFieldTransforms()
          .stream()
          .map(CatalogDiffConverters::fieldTransformToApi)
          .toList());
    } else {
      return Optional.empty();
    }
  }

  public static FieldTransform fieldTransformToApi(final io.airbyte.protocol.models.transform_models.FieldTransform transform) {
    return new FieldTransform()
        .transformType(Enums.convertTo(transform.getTransformType(), FieldTransform.TransformTypeEnum.class))
        .addField(addFieldToApi(transform).orElse(null))
        .removeField(removeFieldToApi(transform).orElse(null))
        .updateFieldSchema(updateFieldToApi(transform).orElse(null));
  }

  private static Optional<FieldNameAndSchema> addFieldToApi(final io.airbyte.protocol.models.transform_models.FieldTransform transform) {
    if (transform.getTransformType() == FieldTransformType.ADD_FIELD) {
      return Optional.of(new FieldNameAndSchema()
          .fieldName(transform.getAddFieldTransform().getFieldName())
          .fieldSchema(transform.getAddFieldTransform().getSchema()));
    } else {
      return Optional.empty();
    }
  }

  private static Optional<FieldNameAndSchema> removeFieldToApi(final io.airbyte.protocol.models.transform_models.FieldTransform transform) {
    if (transform.getTransformType() == FieldTransformType.REMOVE_FIELD) {
      return Optional.of(new FieldNameAndSchema()
          .fieldName(transform.getRemoveFieldTransform().getFieldName())
          .fieldSchema(transform.getRemoveFieldTransform().getSchema()));
    } else {
      return Optional.empty();
    }
  }

  private static Optional<FieldSchemaUpdate> updateFieldToApi(final io.airbyte.protocol.models.transform_models.FieldTransform transform) {
    if (transform.getTransformType() == FieldTransformType.UPDATE_FIELD) {
      return Optional.of(new FieldSchemaUpdate()
          .fieldName(transform.getUpdateFieldTransform().getFieldName())
          .oldSchema(transform.getUpdateFieldTransform().getOldSchema())
          .newSchema(transform.getUpdateFieldTransform().getNewSchema()));
    } else {
      return Optional.empty();
    }
  }

}
