/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import io.airbyte.protocol.models.CommonField;

/**
 * A no-op implementation that always returns zero.
 */
public class ZeroFieldSizeEstimator<Datatype> implements FieldSizeEstimator<Datatype> {

  @Override
  public long getByteSize(final CommonField<Datatype> field) {
    return 0L;
  }

}
