package io.airbyte.cdk.gradle

import org.gradle.testkit.runner.GradleRunner
import org.gradle.testkit.runner.TaskOutcome
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir
import java.io.File
import java.nio.file.Files
import java.nio.file.StandardCopyOption
import kotlin.test.assertEquals

/**
 * Tests for the check task in the airbyte-cdk/build.gradle file.
 * This test verifies that the check task correctly includes:
 * 1. All CDK subprojects
 * 2. Connector projects with 'cdk = local'
 * 3. Connector projects with 'useLocalCdk = true'
 */
class CheckTaskTest {

    @TempDir
    lateinit var testProjectDir: File

    @BeforeEach
    fun setup() {
        // Copy test project files from resources
        copyResourceDir("test-project", testProjectDir)
    }

    /**
     * Copies a directory from the test resources to the test project directory.
     */
    private fun copyResourceDir(resourcePath: String, targetDir: File) {
        val resourceUrl = javaClass.classLoader.getResource(resourcePath)
            ?: throw IllegalArgumentException("Resource not found: $resourcePath")

        val resourceDir = File(resourceUrl.toURI())
        resourceDir.walkTopDown().forEach { sourceFile ->
            if (sourceFile.isFile) {
                val relativePath = sourceFile.relativeTo(resourceDir).path
                val targetFile = File(targetDir, relativePath)
                targetFile.parentFile.mkdirs()
                sourceFile.copyTo(targetFile, overwrite = true)
            }
        }
    }

    @Test
    fun `check task includes CDK subprojects and local connectors`() {
        // Run the check task
        val result = GradleRunner.create()
            .withProjectDir(testProjectDir)
            .withArguments(":airbyte-cdk:check", "--dry-run")
            .withDebug(true)
            .build()

        // When using --dry-run, the task outcome is null because the task isn't actually executed
        // We only care about the task dependencies in the output

        // Verify that the output contains the expected task dependencies
        val output = result.output
        assert(output.contains(":airbyte-cdk:subproject:check")) { "CDK subproject check task should be included" }
        assert(output.contains(":airbyte-integrations:connectors:local-connector:check")) { "Local connector check task should be included" }
        assert(!output.contains(":airbyte-integrations:connectors:non-local-connector:check")) { "Non-local connector check task should not be included" }
        assert(output.contains(":airbyte-integrations:connectors:java-local-connector:check")) { "Java local connector check task should be included" }
        assert(!output.contains(":airbyte-integrations:connectors:java-non-local-connector:check")) { "Java non-local connector check task should not be included" }
    }
}
