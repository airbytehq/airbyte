/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql.config_spec

import com.fasterxml.jackson.annotation.*
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "ssl_method")
@JsonSubTypes(
    JsonSubTypes.Type(
        value = MsSqlServerEncryptionDisabledConfigurationSpecification::class,
        name = "unencrypted"
    ),
    JsonSubTypes.Type(
        value =
            MsSqlServerEncryptionRequiredTrustServerCertificateConfigurationSpecification::class,
        name = "encrypted_trust_server_certificate"
    ),
    JsonSubTypes.Type(value = SslVerifyCertificate::class, name = "encrypted_verify_certificate"),
)
@JsonSchemaTitle("Encryption")
@JsonSchemaDescription("The encryption method which is used when communicating with the database.")
sealed interface MsSqlServerEncryptionConfigurationSpecification

@JsonSchemaTitle("Unencrypted")
@JsonSchemaDescription(
    "Data transfer will not be encrypted.",
)
data object MsSqlServerEncryptionDisabledConfigurationSpecification :
    MsSqlServerEncryptionConfigurationSpecification

@JsonSchemaTitle("Encrypted (trust server certificate)")
@JsonSchemaDescription(
    "Use the certificate provided by the server without verification. (For testing purposes only!)"
)
data object MsSqlServerEncryptionRequiredTrustServerCertificateConfigurationSpecification :
    MsSqlServerEncryptionConfigurationSpecification

@JsonSchemaTitle("Encrypted (verify certificate)")
@JsonSchemaDescription("Verify and use the certificate provided by the server.")
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class SslVerifyCertificate : MsSqlServerEncryptionConfigurationSpecification {
    @JsonProperty("hostNameInCertificate")
    @JsonSchemaTitle("Host Name In Certificate")
    @JsonPropertyDescription(
        "Specifies the host name of the server. The value of this property must match the subject property of the certificate.",
    )
    @JsonSchemaInject(json = """{"order":0}""")
    var hostNameInCertificate: String? = null

    @JsonProperty("certificate", required = false)
    @JsonSchemaTitle("Certificate")
    @JsonPropertyDescription(
        "certificate of the server, or of the CA that signed the server certificate",
    )
    @JsonSchemaInject(json = """{"order":1,"airbyte_secret":true,"multiline":true}""")
    var certificate: String? = null
}

class MicronautPropertiesFriendlyMsSqlServerEncryption {
    var mode: String = "preferred"
    var certificate: String? = null

    @JsonValue
    fun asEncryption(): MsSqlServerEncryptionConfigurationSpecification =
        when (mode) {
            "preferred" -> MsSqlServerEncryptionDisabledConfigurationSpecification
            "required" ->
                MsSqlServerEncryptionRequiredTrustServerCertificateConfigurationSpecification
            "verify_ca" -> SslVerifyCertificate().also { it.certificate = certificate!! }
            else -> throw ConfigErrorException("invalid value $mode")
        }
}
