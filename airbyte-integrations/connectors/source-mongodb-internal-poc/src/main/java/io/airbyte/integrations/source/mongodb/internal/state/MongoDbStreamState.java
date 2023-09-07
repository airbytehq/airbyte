/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.state;

/*
 * TODO replace `isObjectId` with _id enum (ObjectId, String, etc.)
 */
public record MongoDbStreamState(String id) { // , boolean isObjectId) {

}
