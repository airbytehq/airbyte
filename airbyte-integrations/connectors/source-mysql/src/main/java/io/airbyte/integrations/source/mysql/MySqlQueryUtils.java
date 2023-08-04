package io.airbyte.integrations.source.mysql;

public class MySqlQueryUtils {
  public record TableSizeInfo(Long tableSize, Long numRows) { }
}
