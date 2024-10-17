/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.nio.file.Files
import java.nio.file.Path

class MockDestinationConfiguration : DestinationConfiguration()

@Singleton
class MockDestinationSpecification : ConfigurationSpecification() {
    companion object {
        val configPath: Path

        init {
            Files.createDirectories(Path.of("/tmp/airbyte_tests/"))
            val tmpDir = Files.createTempDirectory(Path.of("/tmp/airbyte_tests/"), "test")
            tmpDir.toFile().deleteOnExit()
            val configFile =
                Files.write(tmpDir.resolve("config.json"), "{}".toByteArray(Charsets.UTF_8))
            configPath = configFile.toAbsolutePath()
        }
    }
}

@Singleton
class MockDestinationConfigurationFactory :
    DestinationConfigurationFactory<MockDestinationSpecification, MockDestinationConfiguration> {

    override fun makeWithoutExceptionHandling(
        pojo: MockDestinationSpecification
    ): MockDestinationConfiguration {
        return MockDestinationConfiguration()
    }
}

@Factory
class MockDestinationConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): MockDestinationConfiguration {
        return config as MockDestinationConfiguration
    }
}
