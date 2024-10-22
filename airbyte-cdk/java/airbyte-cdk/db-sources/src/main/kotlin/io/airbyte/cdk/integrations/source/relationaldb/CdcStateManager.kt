/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb

import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import java.util.*
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class CdcStateManager(
    private val initialState: CdcState?,
    initialStreamsSynced: Set<AirbyteStreamNameNamespacePair>?,
    stateMessage: AirbyteStateMessage?
) {
    val initialStreamsSynced: Set<AirbyteStreamNameNamespacePair>?
    val rawStateMessage: AirbyteStateMessage?
    private var currentState: CdcState?

    init {
        this.currentState = initialState
        this.initialStreamsSynced =
            if (initialStreamsSynced != null) Collections.unmodifiableSet(initialStreamsSynced)
            else null
        this.rawStateMessage = stateMessage
        LOGGER.info("Initialized CDC state")
    }

    var cdcState: CdcState?
        get() = if (currentState != null) Jsons.clone(currentState!!) else null
        set(state) {
            this.currentState = state
        }

    override fun toString(): String {
        return "CdcStateManager{" +
            "initialState=" +
            initialState +
            ", currentState=" +
            currentState +
            '}'
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(CdcStateManager::class.java)
    }
}
