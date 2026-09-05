/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.fakesource

import io.airbyte.cdk.command.SpecSchemaSnapshotTest

/**
 * Guards the schema generated for the CDK's own reference source specification. Between this and
 * the JDBC toolkit snapshots, the shared annotation surface — titles, descriptions, defaults, raw
 * JSON injection, unique-item arrays, and `oneOf` from sealed interfaces — is covered without
 * needing any connector to be built.
 */
class FakeSourceSpecSchemaSnapshotTest :
    SpecSchemaSnapshotTest(FakeSourceConfigurationSpecification::class.java)
