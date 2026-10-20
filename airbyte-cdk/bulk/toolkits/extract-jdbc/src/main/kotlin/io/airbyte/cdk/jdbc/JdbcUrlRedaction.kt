/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.jdbc

private val JDBC_URL_CREDENTIAL_PARAMETER =
    Regex(
        """([;?&(]\s*[^;?&()=]*?(?:password|passwd|pwd|secret|token|api[_-]?key|credential|private[_-]?key|access[_-]?key|passphrase)[^;?&()=]*=)(\{[^}]*}|[^;&)]*)""",
        RegexOption.IGNORE_CASE,
    )

private val JDBC_URL_USERINFO_PASSWORD = Regex("""(?<=//)([^:/?#@]+):[^/?#@]*@""")

/** Redacts credential-looking parameters and URL userinfo from a JDBC URL. */
fun redactJdbcUrl(jdbcUrl: String): String {
    val redactedParameters =
        JDBC_URL_CREDENTIAL_PARAMETER.replace(jdbcUrl) { match -> "${match.groupValues[1]}****" }
    return JDBC_URL_USERINFO_PASSWORD.replace(redactedParameters) { match ->
        "${match.groupValues[1]}:****@"
    }
}
