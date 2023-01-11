/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

import static io.airbyte.integrations.destination.s3.S3DestinationConstants.NAME_TRANSFORMER;

import io.airbyte.protocol.models.v0.AirbyteStream;
import java.util.LinkedList;
import java.util.List;

public class S3OutputPathHelper {

  public static String getOutputPrefix(final String bucketPath, final AirbyteStream stream) {
    return getOutputPrefix(bucketPath, stream.getNamespace(), stream.getName());
  }

  /**
   * Prefix: &lt;bucket-path&gt;/&lt;source-namespace-if-present&gt;/&lt;stream-name&gt;
   */
  // Prefix: <bucket-path>/<source-namespace-if-present>/<stream-name>
  public static String getOutputPrefix(final String bucketPath, final String namespace, final String streamName) {
    final List<String> paths = new LinkedList<>();

    if (bucketPath != null) {
      paths.add(bucketPath);
    }
    if (namespace != null) {
      paths.add(NAME_TRANSFORMER.convertStreamName(namespace));
    }
    paths.add(NAME_TRANSFORMER.convertStreamName(streamName));

    return String.join("/", paths).replaceAll("/+", "/");
  }

}
