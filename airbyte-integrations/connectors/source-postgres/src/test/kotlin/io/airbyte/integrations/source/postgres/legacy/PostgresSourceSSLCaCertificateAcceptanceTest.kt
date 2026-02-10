/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.legacy

import com.google.common.collect.ImmutableMap

class PostgresSourceSSLCaCertificateAcceptanceTest :
    AbstractPostgresSourceSSLCertificateAcceptanceTest() {
    override val certificateConfiguration: MutableMap<Any?, Any?>
        get() =
            ImmutableMap.builder<Any?, Any?>()
                .put("mode", "verify-ca")
                .put("ca_certificate", testdb.certificates.caCertificate)
                .put("client_key_password", PASSWORD)
                .build()
}
