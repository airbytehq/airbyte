/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.sourceTesting.cleanup

import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.test.fixtures.cleanup.TestAssetResourceNamer
import io.airbyte.cdk.test.fixtures.connector.JdbcTestDbExecutor
import io.airbyte.cdk.test.fixtures.connector.SqlDialect
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Clock

/**
 * Implementation of TestAssetCleaner for JDBC connections. This cleans up test assets (tables,
 * namespaces) from previous test runs by querying database metadata and identifying test objects by
 * their naming convention.
 */
class JdbcTestAssetCleaner(
    private val executor: JdbcTestDbExecutor,
    private val sqlDialect: SqlDialect,
    private val metadataQuerier: MetadataQuerier,
    private val testAssetResourceNamer: TestAssetResourceNamer,
    clock: Clock,
) : TestAssetCleaner(clock) {

    private val log = KotlinLogging.logger {}

    override val assetName = executor.assetName

    override fun cleanupOldTestAssets() {
        cleanupOldTestTables()
        cleanupOldTestNamespaces()
    }

    override fun close() {
        executor.close()
    }

    private fun cleanupOldTestTables() {
        val allTestTables = findAllTestTables()

        for ((namespace, tables) in allTestTables) {
            for (table in tables) {
                if (testAssetResourceNamer.millisFromName(table).tooOld()) {
                    val dropQuery = sqlDialect.buildDropTableQuery(namespace, table)
                    log.info { "Dropping old test table: $namespace.$table" }
                    executor.executeUpdate(dropQuery)
                }
            }
        }
    }

    private fun cleanupOldTestNamespaces() {
        val testNamespaces = findAllTestNamespaces()

        for (namespace in testNamespaces) {
            if (testAssetResourceNamer.millisFromName(namespace).tooOld()) {
                val dropQuery = sqlDialect.buildDropNamespaceQuery(namespace)
                log.info { "Dropping old test namespace: $namespace" }
                executor.executeUpdate(dropQuery)
            }
        }
    }

    /** Finds all test tables in the database. Returns a map of namespace to list of table names. */
    private fun findAllTestTables(): Map<String, List<String>> {
        return metadataQuerier
            .streamNames(null)
            .filter { testAssetResourceNamer.millisFromName(it.namespace!!) != null }
            .filter { testAssetResourceNamer.millisFromName(it.name) != null }
            .groupBy(
                keySelector = { it.namespace!! },
                valueTransform = { it.name },
            )
    }

    /** Finds all test namespaces in the database. Returns a list of namespace names. */
    private fun findAllTestNamespaces(): List<String> {
        return metadataQuerier.streamNamespaces().filter {
            testAssetResourceNamer.millisFromName(it) != null
        }
    }
}
