package io.airbyte.integrations.base.destination.typing_deduping;

import static java.util.stream.Collectors.joining;

import java.util.stream.Stream;
import org.apache.commons.lang3.StringUtils;

public record NameAndNamespacePair(String namespace, String tableName) {

  public Stream<String> stream() {
    return Stream.of(namespace, tableName);
  }

  public String combinedAndQuoted(String quote) {
    return this.stream()
        .map(part -> StringUtils.wrap(part, quote))
        .collect(joining("."));
  }
}
