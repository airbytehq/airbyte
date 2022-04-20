package io.airbyte.integrations.source.relationaldb;

import io.airbyte.protocol.models.CommonField;

public class ZeroFieldSizeEstimator<Datatype> implements FieldSizeEstimator<Datatype> {

  @Override
  public long getByteSize(final CommonField<Datatype> field) {
    return 0L;
  }

}
