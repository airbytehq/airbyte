/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.datagen

import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.util.Jsons
import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * Snapshots the JSON schema generated for this connector's specification class against a checked-in
 * golden file. Generation is a pure function of the class, so this needs no Micronaut context, no
 * connector process, and no credentials — it runs on every build and is the safety net for changes
 * to the CDK's schema generator.
 *
 * To accept an intended change, re-run with `AIRBYTE_SPEC_SNAPSHOT_UPDATE=true` and commit the diff.
 * The snapshot does not self-update on a normal run: a golden that rewrites itself is not a
 * baseline.
 *
 * Duplicated per connector because connectors build against a published CDK jar (`cdkVersion` in
 * gradle.properties) and cannot see a fixture that only exists in CDK source. Collapse onto
 * [io.airbyte.cdk.command.SpecSchemaSnapshotTest] once that fixture ships in a released CDK.
 */
class DataGenSourceSpecSchemaSnapshotTest {
    @Test
    fun testSpecSchemaSnapshot() {
        val specClass = DataGenSourceConfigurationSpecification::class.java
        val actual =
            Jsons.writerWithDefaultPrettyPrinter()
                .writeValueAsString(ValidatedJsonUtils.generateAirbyteJsonSchema(specClass)) + "\n"
        val goldenPath: Path =
            Path.of("src/test/resources/spec-schema-snapshots/${specClass.simpleName}.json")

        val update =
            System.getenv("AIRBYTE_SPEC_SNAPSHOT_UPDATE").toBoolean() ||
                System.getProperty("airbyte.specSnapshot.update").toBoolean()
        if (update || !Files.exists(goldenPath)) {
            Files.createDirectories(goldenPath.parent)
            Files.writeString(goldenPath, actual)
            Assertions.assertTrue(update, "No snapshot existed; wrote $goldenPath. Commit it.")
            return
        }

        if (Files.readString(goldenPath) == actual) {
            return
        }
        val actualPath: Path = goldenPath.resolveSibling("${specClass.simpleName}.json.actual")
        Files.writeString(actualPath, actual)
        Assertions.fail<Unit>(
            "Generated JSON schema for ${specClass.name} no longer matches $goldenPath.\n" +
                "Wrote the generated schema to $actualPath; run `diff $goldenPath $actualPath`.\n" +
                "If the change is intended, re-run with AIRBYTE_SPEC_SNAPSHOT_UPDATE=true.",
        )
    }
}
