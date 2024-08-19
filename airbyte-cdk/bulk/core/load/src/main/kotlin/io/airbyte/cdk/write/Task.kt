package io.airbyte.cdk.write

abstract class Task {
    data class Concurrency(val id: String, val limit: Int)

    open val concurrency: Concurrency? = null

    abstract suspend fun execute()
}
