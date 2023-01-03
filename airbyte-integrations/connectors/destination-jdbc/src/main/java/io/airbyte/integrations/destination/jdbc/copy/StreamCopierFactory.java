/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;

public interface StreamCopierFactory<T> {

  StreamCopier create(String configuredSchema,
                      T config,
                      String stagingFolder,
                      ConfiguredAirbyteStream configuredStream,
                      ExtendedNameTransformer nameTransformer,
                      JdbcDatabase db,
                      SqlOperations sqlOperations);

  static String getSchema(final String namespace, final String configuredSchema, final ExtendedNameTransformer nameTransformer) {
    if (namespace != null) {
      return nameTransformer.convertStreamName(namespace);
    } else {
      return nameTransformer.convertStreamName(configuredSchema);
    }
  }

}
