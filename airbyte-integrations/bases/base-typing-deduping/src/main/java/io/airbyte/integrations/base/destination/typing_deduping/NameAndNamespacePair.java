package io.airbyte.integrations.base.destination.typing_deduping;

public record NameAndNamespacePair(String namespace, String tableName) { }
