/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

class PostgresSourceSSLFullCertificateAcceptanceTest :
    AbstractPostgresSourceSSLCertificateAcceptanceTest() {
    override val certificateConfiguration: MutableMap<Any?, Any?>
        get() =
            mutableMapOf(
                "mode" to "verify-ca",
                "ca_certificate" to testdb.certificates.caCertificate,
                "client_certificate" to testdb.certificates.clientCertificate,
                "client_key" to testdb.certificates.clientKey,
                "client_key_password" to PASSWORD,
            )
}
