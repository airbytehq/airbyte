/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.legacy

import io.airbyte.cdk.test.fixtures.legacy.SourceAcceptanceTest
import io.airbyte.cdk.test.fixtures.legacy.SshHelpers
import io.airbyte.protocol.models.v0.ConnectorSpecification
import java.util.*

abstract class AbstractPostgresSourceAcceptanceTest : SourceAcceptanceTest() {
    override val imageName: String
        get() = "airbyte/source-postgres:dev"

    @get:Throws(Exception::class)
    override val spec: ConnectorSpecification
        get() =
            SshHelpers.getSpecAndInjectSsh(
                Optional.empty()
                /*Optional.of<String?>(
                    "security",
                ),*/
                )
}
