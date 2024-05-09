/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.state;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public record MongoDbStreamState(String id, InitialSnapshotStatus status, IdType idType) {}
