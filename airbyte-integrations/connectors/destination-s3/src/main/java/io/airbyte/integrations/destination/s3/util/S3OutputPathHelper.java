/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

import static io.airbyte.integrations.destination.s3.S3DestinationConstants.NAME_TRANSFORMER;

import io.airbyte.protocol.models.AirbyteStream;
import java.util.LinkedList;
import java.util.List;

public class S3OutputPathHelper {

  public static String getOutputPrefix(String bucketPath, AirbyteStream stream) {
    return getOutputPrefix(bucketPath, stream.getNamespace(), stream.getName());
  }

  /**
   * Prefix: <bucket-path>/<source-namespace-if-present>/<stream-name>
   */
  public static String getOutputPrefix(String bucketPath, String namespace, String streamName) {
    List<String> paths = new LinkedList<>();

    if (bucketPath != null) {
      paths.add(bucketPath);
    }
    if (namespace != null) {
      paths.add(NAME_TRANSFORMER.convertStreamName(namespace));
    }
    paths.add(NAME_TRANSFORMER.convertStreamName(streamName));

    return String.join("/", paths);
  }

}
