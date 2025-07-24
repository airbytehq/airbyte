package io.airbyte.cdk.load.check


interface DestinationCheckerV2 {
    fun check()
    fun cleanup() {}
}
