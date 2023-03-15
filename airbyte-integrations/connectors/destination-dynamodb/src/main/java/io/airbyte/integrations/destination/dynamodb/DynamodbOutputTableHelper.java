/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dynamodb;

import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.protocol.models.v0.AirbyteStream;
import java.util.LinkedList;
import java.util.List;

public class DynamodbOutputTableHelper {

  public static String getOutputTableName(final String tableNamePrefix, final AirbyteStream stream) {
    return getOutputTableName(tableNamePrefix, stream.getNamespace(), stream.getName());
  }

  public static String getOutputTableName(final String tableNamePrefix, final String namespace, final String streamName) {
    final List<String> paths = new LinkedList<>();

    if (tableNamePrefix != null) {
      paths.add(tableNamePrefix);
    }
    if (namespace != null) {
      paths.add(new StandardNameTransformer().convertStreamName(namespace));
    }
    if (streamName != null) {
      paths.add(new StandardNameTransformer().convertStreamName(streamName));
    }

    return String.join("_", paths);
  }

}
