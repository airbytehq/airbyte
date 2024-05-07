/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.process

import io.airbyte.workers.exception.TestHarnessException
import java.nio.file.Path

/**
 * This interface provides an abstraction for launching a container that implements the Airbyte
 * Protocol. Such containers implement each method that is defined in the Protocol. This class,
 * provides java methods to invoke the methods on these containers.
 *
 * Each method takes in a jobRoot that is a directory where the worker that runs the method can use
 * as temporary file system storage.
 */
interface IntegrationLauncher {
    @Throws(TestHarnessException::class) fun spec(jobRoot: Path): Process

    @Throws(TestHarnessException::class)
    fun check(jobRoot: Path, configFilename: String, configContents: String): Process

    @Throws(TestHarnessException::class)
    fun discover(jobRoot: Path, configFilename: String, configContents: String): Process

    @Throws(TestHarnessException::class)
    fun read(
        jobRoot: Path,
        configFilename: String?,
        configContents: String?,
        catalogFilename: String?,
        catalogContents: String?,
        stateFilename: String?,
        stateContents: String?
    ): Process?

    @Throws(TestHarnessException::class)
    fun read(
        jobRoot: Path,
        configFilename: String?,
        configContents: String?,
        catalogFilename: String?,
        catalogContents: String?
    ): Process? {
        return read(
            jobRoot,
            configFilename,
            configContents,
            catalogFilename,
            catalogContents,
            null,
            null
        )
    }

    @Throws(TestHarnessException::class)
    fun write(
        jobRoot: Path,
        configFilename: String,
        configContents: String,
        catalogFilename: String,
        catalogContents: String,
        additionalEnvironmentVariables: Map<String, String>
    ): Process?
}
