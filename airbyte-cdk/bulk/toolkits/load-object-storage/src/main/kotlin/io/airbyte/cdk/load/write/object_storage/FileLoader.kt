package io.airbyte.cdk.load.write.object_storage

/**
 * [FileLoader] is for the use case where the client wants to move whole files directly into
 * object storage. Incoming records contain file metadata, and the file itself is stored in a
 * staging directory on the pod where the connector is running.
 *
 * Usage:
 *
 * Declare a bean of type [FileLoader] and configure as per the documentation in [ObjectLoader].
 * (The only exception is the that [io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration.fileNamePattern]
 * will be ignored in favor of the filename provided in the file metadata message.)
 */
interface FileLoader: ObjectLoader
