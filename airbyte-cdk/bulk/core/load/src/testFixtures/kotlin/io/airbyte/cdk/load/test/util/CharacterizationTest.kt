/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
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
        Assertions.assertEquals(
            goldenFileContents,
            actualContents,
            "File contents did not match previous version. Inspect the `git diff` and commit the change if this is intended.",
        )
    }
}
