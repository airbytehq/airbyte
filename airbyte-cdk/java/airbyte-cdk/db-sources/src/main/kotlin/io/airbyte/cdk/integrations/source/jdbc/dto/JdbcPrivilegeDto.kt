/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.jdbc.dto

import com.google.common.base.Objects

/** The class to store values from privileges table */
class JdbcPrivilegeDto(
    val grantee: String?,
    val tableName: String?,
    val schemaName: String?,
    val privilege: String?
) {
    class JdbcPrivilegeDtoBuilder {
        private var grantee: String? = null
        private var tableName: String? = null
        private var schemaName: String? = null
        private var privilege: String? = null

        fun grantee(grantee: String?): JdbcPrivilegeDtoBuilder {
            this.grantee = grantee
            return this
        }

        fun tableName(tableName: String?): JdbcPrivilegeDtoBuilder {
            this.tableName = tableName
            return this
        }

        fun schemaName(schemaName: String?): JdbcPrivilegeDtoBuilder {
            this.schemaName = schemaName
            return this
        }

        fun privilege(privilege: String?): JdbcPrivilegeDtoBuilder {
            this.privilege = privilege
            return this
        }

        fun build(): JdbcPrivilegeDto {
            return JdbcPrivilegeDto(grantee, tableName, schemaName, privilege)
        }
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) {
            return true
        }
        if (other == null || javaClass != other.javaClass) {
            return false
        }
        val that = other as JdbcPrivilegeDto
        return (Objects.equal(grantee, that.grantee) &&
            Objects.equal(tableName, that.tableName) &&
            Objects.equal(schemaName, that.schemaName) &&
            Objects.equal(privilege, that.privilege))
    }

    override fun hashCode(): Int {
        return Objects.hashCode(grantee, tableName, schemaName, privilege)
    }

    override fun toString(): String {
        return "JdbcPrivilegeDto{" +
            "grantee='" +
            grantee +
            '\'' +
            ", columnName='" +
            tableName +
            '\'' +
            ", schemaName='" +
            schemaName +
            '\'' +
            ", privilege='" +
            privilege +
            '\'' +
            '}'
    }

    companion object {
        @JvmStatic
        fun builder(): JdbcPrivilegeDtoBuilder {
            return JdbcPrivilegeDtoBuilder()
        }
    }
}
