/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dynamodb;

import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.protocol.models.AirbyteStream;
import java.util.LinkedList;
import java.util.List;

public class DynamodbOutputTableHelper {

  public static String getOutputTableName(String tableName, AirbyteStream stream) {
    return getOutputTableName(tableName, stream.getNamespace(), stream.getName());
  }

  public static String getOutputTableName(String tableName, String namespace, String streamName) {
    List<String> paths = new LinkedList<>();

    if (tableName != null) {
      paths.add(tableName);
    }
    if (namespace != null) {
      paths.add(new ExtendedNameTransformer().convertStreamName(namespace));
    }
    if (streamName != null) {
      paths.add(new ExtendedNameTransformer().convertStreamName(streamName));
    }

    return String.join("_", paths);
  }

}
