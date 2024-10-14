package io.airbyte.cdk.load.file


/** Represents a remote object containing persisted records. */
interface RemoteObject<T> {
    val key: String
    val bucketConfig: T
}


