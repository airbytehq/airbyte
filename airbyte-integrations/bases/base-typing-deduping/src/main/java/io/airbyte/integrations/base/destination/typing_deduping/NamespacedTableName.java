/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

// yet another namespace, name combo class
public record NamespacedTableName(String namespace, String tableName) {

}
