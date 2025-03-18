/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.teradata.util

interface TeradataConstants {
    companion object {
        const val DRIVER_CLASS: String = "com.teradata.jdbc.TeraDriver"
        const val DEFAULT_SCHEMA_NAME: String = "def_airbyte_db"
        const val PARAM_MODE: String = "mode"
        const val PARAM_SSL: String = "ssl"
        const val PARAM_SSL_MODE: String = "ssl_mode"
        const val PARAM_SSLMODE: String = "sslmode"
        const val PARAM_SSLCA: String = "sslca"
        const val ENCRYPTDATA: String = "ENCRYPTDATA"
        const val ENCRYPTDATA_ON: String = "ON"
        const val CA_CERTIFICATE: String = "ca.pem"
        const val ALLOW: String = "allow"
        const val REQUIRE: String = "require"
        const val VERIFY_CA: String = "verify-ca"
        const val VERIFY_FULL: String = "verify-full"
        const val CA_CERT_KEY: String = "ssl_ca_certificate"
    }
}
