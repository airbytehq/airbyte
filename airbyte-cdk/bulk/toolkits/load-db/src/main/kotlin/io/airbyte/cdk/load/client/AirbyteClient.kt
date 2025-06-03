package io.airbyte.cdk.load.client

abstract class AirbyteClient {
    // TODO: missing namespace
    abstract fun getNumberOfRecordsInTable(database: String, table: String): Long
}
