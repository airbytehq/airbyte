/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.legacy

import io.airbyte.integrations.source.postgres.legacy.testFixtures.PostgresTestDatabase

class PostgresSourceAcceptanceLegacyCtidTest : PostgresSourceAcceptanceTest() {
    override val serverImage: PostgresTestDatabase.BaseImage
        get() = PostgresTestDatabase.BaseImage.POSTGRES_12
}
