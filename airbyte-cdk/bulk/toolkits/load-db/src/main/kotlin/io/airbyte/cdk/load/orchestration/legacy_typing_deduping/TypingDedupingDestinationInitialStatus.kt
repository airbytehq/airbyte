package io.airbyte.cdk.load.orchestration.legacy_typing_deduping

import io.airbyte.cdk.load.orchestration.DestinationInitialStatus

data class TypingDedupingDestinationInitialStatus(
    val isFinalTablePresent: Boolean,
    // TODO other stuff
) : DestinationInitialStatus
