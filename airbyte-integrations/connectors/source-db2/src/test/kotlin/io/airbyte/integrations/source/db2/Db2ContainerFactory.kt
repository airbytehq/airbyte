/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.db2

import io.airbyte.cdk.testcontainers.TestContainerFactory
import io.airbyte.integrations.source.db2.config.Db2SourceConfigurationSpecification
import io.github.oshai.kotlinlogging.KotlinLogging
import org.testcontainers.containers.Db2Container
import org.testcontainers.utility.DockerImageName

object Db2ContainerFactory {
    private val log = KotlinLogging.logger {}
    private val IMAGE_NAME = DockerImageName.parse("icr.io/db2_community/db2")

    init {
        TestContainerFactory.register(IMAGE_NAME, ::LicensedContainer)
    }

    // This constructor allows us to accept an EULA required by the IBM Db2 image.
    // See the "EULA Acceptance" section in the Testcontainers docs for more info:
    // https://java.testcontainers.org/modules/databases/db2/
    private class LicensedContainer(dockerImageName: DockerImageName) :
        Db2Container(dockerImageName) {
        init {
            this.acceptLicense()
        }
    }

    fun exclusive(): Db2Container {
        return TestContainerFactory.exclusive(IMAGE_NAME)
    }

    fun shared(): Db2Container {
        return TestContainerFactory.shared(IMAGE_NAME)
    }

    @JvmStatic
    fun configSpecification(db2Container: Db2Container): Db2SourceConfigurationSpecification =
        Db2SourceConfigurationSpecification().apply {
            host = db2Container.host
            port = db2Container.firstMappedPort
            database = db2Container.databaseName
            username = db2Container.username
            password = db2Container.password
            jdbcUrlParams = ""
            schemas = listOf(db2Container.username)
            checkpointTargetIntervalSeconds = 60
            concurrency = 1
        }
}
