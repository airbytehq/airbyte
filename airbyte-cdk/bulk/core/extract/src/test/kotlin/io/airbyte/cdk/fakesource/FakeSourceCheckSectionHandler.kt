/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.fakesource

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.check.CheckSectionHandler
import jakarta.inject.Singleton

/** [CheckSectionHandler] for the fake source: records the sections it was asked to check. */
@Singleton
class FakeSourceCheckSectionHandler : CheckSectionHandler<FakeSourceConfigurationSpecification> {
    val checkedSections: MutableList<String> = mutableListOf()

    override fun check(section: String, pojo: FakeSourceConfigurationSpecification) {
        checkedSections.add(section)
        if (pojo.host == UNREACHABLE_HOST) {
            throw ConfigErrorException("Host '$UNREACHABLE_HOST' cannot be reached.")
        }
    }

    companion object {
        const val UNREACHABLE_HOST = "unreachable"
    }
}
