/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.skeleton_directload.write.typing_deduping

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.orchestration.db.DatabaseHandler
import io.airbyte.cdk.load.orchestration.db.Sql
import io.airbyte.integrations.destination.skeleton_directload.SkeletonDirectLoadClient
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin is hard")
class SkeletonDirectLoadDatabaseHandler(private val skeletonClient: SkeletonDirectLoadClient) :
    DatabaseHandler {

    @Throws(InterruptedException::class) override fun execute(sql: Sql) {}

    override suspend fun createNamespaces(namespaces: Collection<String>) {}
}
