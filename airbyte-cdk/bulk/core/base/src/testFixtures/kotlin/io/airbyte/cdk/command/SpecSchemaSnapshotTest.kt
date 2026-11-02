/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.util.Jsons
import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.DynamicTest
import org.junit.jupiter.api.TestFactory

/**
 * Snapshots the JSON schema that [ValidatedJsonUtils.generateAirbyteJsonSchema] produces for a set
 * of specification classes, and compares it against a checked-in golden file.
 *
 * Schema generation is a pure function of the class, so unlike the per-connector spec tests under
 * `src/test-integration` this needs no Micronaut context, no connector process, and no credentials.
 * That makes it cheap enough to run on every build, which is the point: it is the safety net for
 * changes to the schema generator itself.
 *
 * Goldens live in `src/test/resources/spec-schema-snapshots/<SimpleName>.json`. Key order is
 * significant and is preserved verbatim, because the platform UI renders properties in the order
 * the schema declares them.
 *
 * To accept an intended change, re-run with `-Dairbyte.specSnapshot.update=true` and commit the
 * diff. Snapshots deliberately do not self-update on a normal run — a golden that rewrites itself
 * cannot serve as a baseline.
 */
abstract class SpecSchemaSnapshotTest(
    private val specClasses: List<Class<*>>,
) {
    constructor(vararg specClasses: Class<*>) : this(specClasses.toList())

    @TestFactory
    fun specSchemaSnapshots(): List<DynamicTest> =
        specClasses.map { klazz ->
            DynamicTest.dynamicTest(klazz.simpleName) { assertSnapshotMatches(klazz) }
        }

    private fun assertSnapshotMatches(klazz: Class<*>) {
        val schema: JsonNode = ValidatedJsonUtils.generateAirbyteJsonSchema(klazz)
        val actual: String = Jsons.writerWithDefaultPrettyPrinter().writeValueAsString(schema) + "\n"
        val goldenPath: Path = snapshotDir.resolve("${klazz.simpleName}.json")

        if (updateSnapshots || !Files.exists(goldenPath)) {
            Files.createDirectories(goldenPath.parent)
            Files.writeString(goldenPath, actual)
            if (!updateSnapshots) {
                Assertions.fail<Unit>(
                    "No snapshot existed for ${klazz.name}; wrote one to $goldenPath. " +
                        "Review it and commit it.",
                )
            }
            return
        }

        val expected: String = Files.readString(goldenPath)
        if (expected == actual) {
            return
        }
        // Leave the generated schema on disk so the diff is a normal file comparison.
        val actualPath: Path = goldenPath.resolveSibling("${klazz.simpleName}.json.actual")
        Files.writeString(actualPath, actual)
        Assertions.fail<Unit>(
            "Generated JSON schema for ${klazz.name} no longer matches $goldenPath.\n" +
                "Wrote the generated schema to $actualPath; run `diff $goldenPath $actualPath`.\n" +
                "If the change is intended, re-run with -Dairbyte.specSnapshot.update=true and " +
                "commit the diff.",
        )
    }

    companion object {
        val snapshotDir: Path = Path.of("src/test/resources/spec-schema-snapshots")

        val updateSnapshots: Boolean =
            System.getProperty("airbyte.specSnapshot.update").toBoolean() ||
                System.getenv("AIRBYTE_SPEC_SNAPSHOT_UPDATE").toBoolean()
    }
}
