package io.airbyte.integrations.source.relationaldb;

import io.airbyte.protocol.models.CommonField;

public interface FieldSizeEstimator<Datatype> {

  long getByteSize(final CommonField<Datatype> field);

}
