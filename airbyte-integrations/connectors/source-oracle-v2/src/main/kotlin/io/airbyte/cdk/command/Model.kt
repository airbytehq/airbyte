package io.airbyte.cdk.command

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.util.function.Supplier


/**
 * Connector configuration POJO supertype.
 *
 * This dummy base class is required by Micronaut. Without it, thanks to Java's type erasure, it
 * thinks that the  [ConfigJsonObjectSupplierImpl] implementation of
 * [ConnectorConfigurationJsonObjectSupplier] requires a constructor argument of type [Any].
 *
 * Strictly speaking, this means that the subclasses are not really POJOs anymore...
 */
abstract class ConnectorConfigurationJsonObjectBase

/**
 * Supplies a valid [T] configuration POJO instance, based on the `airbyte.connector.config`
 * Micronaut property values:
 * - either `airbyte.connector.config.json` if it is set (typically by the CLI)
 * = or the other, nested `airbyte.connector.config.*` properties (typically in unit tests)
 *
 * The object is also validated against its [jsonSchema] JSON schema, derived from [valueClass].
 */
interface ConnectorConfigurationJsonObjectSupplier<T : ConnectorConfigurationJsonObjectBase>
    : Supplier<T> {
    val valueClass: Class<T>
    val jsonSchema: JsonNode
}

/**
 * Interface that defines a typed connector configuration.
 *
 * Prefer this or its implementations over the corresponding configuration POJOs;
 * i.e. [ConnectorConfigurationJsonObjectBase] subclasses.
 */
sealed interface ConnectorConfiguration {

    val realHost: String
    val realPort: Int
    val sshTunnel: SshTunnelMethodConfiguration
    val sshConnectionOptions: SshConnectionOptions
}

/** Subtype of [ConnectorConfiguration] for sources. */
interface SourceConnectorConfiguration : ConnectorConfiguration {

    val expectedStateType: AirbyteStateMessage.AirbyteStateType

    val jdbcUrlFmt: String
    val jdbcProperties: Map<String, String>

    val schemas: List<String>
}

interface ConnectorConfigurationSupplier<T : ConnectorConfiguration> : Supplier<T>

interface ConfiguredAirbyteCatalogSupplier : Supplier<ConfiguredAirbyteCatalog>

interface ConnectorInputStateSupplier : Supplier<List<AirbyteStateMessage>>
