/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal;

/*
 * TODO replace `isObjectId` with _id enum (ObjectId, String, etc.)
 */
public record MongodbStreamState(String id) { // , boolean isObjectId) {

}
