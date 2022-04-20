/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import io.airbyte.protocol.models.CommonField;

public interface FieldSizeEstimator<Datatype> {

  /**
   * Return the estimated byte size of a database field.
   */
  long getByteSize(final CommonField<Datatype> field);

}
