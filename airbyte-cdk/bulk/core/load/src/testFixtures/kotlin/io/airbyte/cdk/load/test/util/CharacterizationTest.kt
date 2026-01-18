/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.Assertions

object CharacterizationTest {
    val testResourcesPath: Path = Path.of("src/test-integration/resources")
    fun doAssert(
        goldenFileName: String,
        actualContents: String,
    ) {
        val goldenFilePath = testResourcesPath.resolve(goldenFileName)
        if (!Files.exists(goldenFilePath)) {
            Files.createDirectories(goldenFilePath.parent)
            Files.createFile(goldenFilePath)
        }
        val goldenFileContents = Files.readString(goldenFilePath)
        Files.write(goldenFilePath, actualContents.toByteArray())
        // don't use assertEquals, b/c the output is hard to read.
        // We'll include the actual file path in the assert message.
        Assertions.assertTrue(
            goldenFileContents == actualContents,
            "Contents of $goldenFilePath did not match previous version. Inspect the `git diff` and commit the change if this is intended.",
        )
    }
}
