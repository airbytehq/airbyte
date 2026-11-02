/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import io.airbyte.cdk.h2source.H2SourceConfigurationSpecification

/**
 * Guards the schema generated for the JDBC toolkit's shared specification classes, which every
 * JDBC-based source composes into its own spec. [H2SourceConfigurationSpecification] is the
 * toolkit's concrete reference implementation and exercises the SSH tunnel `oneOf` and the
 * unique-item array annotations.
 */
class JdbcSpecSchemaSnapshotTest :
    SpecSchemaSnapshotTest(
        JdbcSourceConfigurationSpecification::class.java,
        H2SourceConfigurationSpecification::class.java,
    )
