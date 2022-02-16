package io.airbyte.integrations.destination.snowflake;

import java.util.List;
import java.util.StringJoiner;

interface SnowflakeParallelCopyStreamCopier {

  default String generateFilesList(List<String> files) {
    StringJoiner joiner = new StringJoiner(",");
    files.forEach(filename -> joiner.add("'" + filename.substring(filename.lastIndexOf("/") + 1) + "'"));
    return joiner.toString();
  }

  void copyIntoStage(List<String> files);

  String generateBucketPath();
}