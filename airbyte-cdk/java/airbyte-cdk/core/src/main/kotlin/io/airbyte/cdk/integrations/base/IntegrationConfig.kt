/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

import com.google.common.base.Preconditions
import java.nio.file.Path
import java.util.*

class IntegrationConfig
private constructor(
    val command: Command,
    private val configPath: Path?,
    private val catalogPath: Path?,
    private val statePath: Path?
) {
    fun getConfigPath(): Path? {
        Preconditions.checkState(command != Command.SPEC)
        return configPath
    }

    fun getCatalogPath(): Path? {
        Preconditions.checkState(command == Command.READ || command == Command.WRITE)
        return catalogPath
    }

    fun getStatePath(): Optional<Path> {
        Preconditions.checkState(command == Command.READ)
        return Optional.ofNullable(statePath)
    }

    override fun toString(): String {
        return "IntegrationConfig{" +
            "command=" +
            command +
            ", configPath='" +
            configPath +
            '\'' +
            ", catalogPath='" +
            catalogPath +
            '\'' +
            ", statePath='" +
            statePath +
            '\'' +
            '}'
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) {
            return true
        }
        if (other == null || javaClass != other.javaClass) {
            return false
        }
        val that = other as IntegrationConfig
        return command == that.command &&
            configPath == that.configPath &&
            catalogPath == that.catalogPath &&
            statePath == that.statePath
    }

    override fun hashCode(): Int {
        return Objects.hash(command, configPath, catalogPath, statePath)
    }

    companion object {
        fun spec(): IntegrationConfig {
            return IntegrationConfig(Command.SPEC, null, null, null)
        }

        fun check(config: Path): IntegrationConfig {
            Preconditions.checkNotNull(config)
            return IntegrationConfig(Command.CHECK, config, null, null)
        }

        fun discover(config: Path): IntegrationConfig {
            Preconditions.checkNotNull(config)
            return IntegrationConfig(Command.DISCOVER, config, null, null)
        }

        fun read(configPath: Path, catalogPath: Path, statePath: Path?): IntegrationConfig {
            Preconditions.checkNotNull(configPath)
            Preconditions.checkNotNull(catalogPath)
            return IntegrationConfig(Command.READ, configPath, catalogPath, statePath)
        }

        fun write(configPath: Path, catalogPath: Path): IntegrationConfig {
            Preconditions.checkNotNull(configPath)
            Preconditions.checkNotNull(catalogPath)
            return IntegrationConfig(Command.WRITE, configPath, catalogPath, null)
        }
    }
}
