/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.legacy

class PostgresSourceSSLFullCertificateAcceptanceTest :
    AbstractPostgresSourceSSLCertificateAcceptanceTest() {

    override val nameSpace: String
        get() = SCHEMA_NAME

    override val certificateConfiguration: MutableMap<Any?, Any?>
        get() =
            mutableMapOf(
                "mode" to "verify-ca",
                "ca_certificate" to testdb.certificates.caCertificate,
                "client_certificate" to testdb.certificates.clientCertificate,
                "client_key" to testdb.certificates.clientKey,
                "client_key_password" to PASSWORD,
            )

    companion object {
        val SCHEMA_NAME: String = "postgres_source_ssl_full_certificate_acceptance_test"
    }
}
