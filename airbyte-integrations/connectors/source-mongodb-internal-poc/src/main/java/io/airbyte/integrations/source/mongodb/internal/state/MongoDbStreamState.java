/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.state;

public record MongoDbStreamState(String id, InitialSnapshotStatus status, IdType idType) {

}
