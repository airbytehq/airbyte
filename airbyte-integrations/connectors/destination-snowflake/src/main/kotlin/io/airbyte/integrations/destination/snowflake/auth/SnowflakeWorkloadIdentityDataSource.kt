/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.auth

import java.io.IOException
import java.io.PrintWriter
import java.net.URI
import java.net.URLDecoder
import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.nio.file.InvalidPathException
import java.nio.file.Path
import java.sql.Connection
import java.sql.Driver
import java.sql.SQLException
import java.sql.SQLFeatureNotSupportedException
import java.util.Locale
import java.util.Properties
import java.util.logging.Logger
import javax.sql.DataSource

enum class WorkloadIdentityProvider {
    AWS,
    AZURE,
    GCP,
    OIDC,
}

/**
 * The physical connection factory beneath Hikari, not a wrapper around the pool.
 *
 * Snowflake JDBC 3.26.1 accepts an OIDC token but cannot refresh it from a file. Read the projected
 * token for EVERY new physical connection. Never resolve the path to its real path: Kubernetes
 * rotates projected volumes by atomically replacing their symlink target.
 *
 * Only the token path and non-secret connection properties are retained here. Existing Snowflake
 * sessions have their own lifetime; borrowing an existing pooled connection does not read the file.
 * Native AWS/Azure/GCP attestation acquisition is delegated to the Snowflake driver on each login.
 */
internal class SnowflakeWorkloadIdentityDataSource(
    private val jdbcUrl: String,
    connectionProperties: Properties,
    private val provider: WorkloadIdentityProvider,
    tokenFilePath: String?,
    private val driver: Driver,
) : DataSource {
    private val tokenPath = validateTokenPath(provider, tokenFilePath)
    private val baseProperties =
        Properties().apply {
            putAll(connectionProperties)
            // Include defaults, if any, without converting non-string JDBC property values.
            connectionProperties.stringPropertyNames().forEach { name ->
                putIfAbsent(name, connectionProperties.getProperty(name))
            }
        }

    @Volatile private var writer: PrintWriter? = null
    @Volatile private var loginTimeoutSeconds: Int? = null

    init {
        validateJdbcUrl(jdbcUrl)
        baseProperties.forEach { key, value ->
            require(key is String) { "Workload identity JDBC property names must be strings." }
            val name = normalizeProperty(key)
            require(name !in AUTHENTICATION_PROPERTIES && name !in ENDPOINT_PROPERTIES) {
                "Do not supply authentication or endpoint overrides alongside workload identity federation."
            }
            validateSsl(name, value.toString())
        }
    }

    override fun getConnection(): Connection {
        // A separate object per connection prevents both races and retaining a stale token in
        // Hikari's configuration. The driver may keep its own login state for the resulting
        // session.
        val properties =
            Properties().apply {
                putAll(baseProperties)
                setProperty("authenticator", "WORKLOAD_IDENTITY")
                setProperty("workloadIdentityProvider", provider.name)
                loginTimeoutSeconds?.let { setProperty("loginTimeout", it.toString()) }
                tokenPath?.let { setProperty("token", readToken(it)) }
            }
        return driver.connect(jdbcUrl, properties)
            ?: throw SQLException("The Snowflake driver rejected the JDBC URL.", "08001")
    }

    override fun getConnection(username: String?, password: String?): Connection {
        if (username != null || password != null) {
            throw SQLFeatureNotSupportedException(
                "Per-connection username/password overrides are not supported for workload identity."
            )
        }
        return getConnection()
    }

    override fun getLogWriter(): PrintWriter? = writer

    override fun setLogWriter(out: PrintWriter?) {
        // Store for the DataSource contract; never write credentials or connection properties.
        writer = out
    }

    override fun setLoginTimeout(seconds: Int) {
        if (seconds < 0) {
            throw SQLException("Login timeout must not be negative.", "HY092")
        }
        loginTimeoutSeconds = seconds
    }

    override fun getLoginTimeout(): Int = loginTimeoutSeconds ?: 0

    override fun getParentLogger(): Logger = Logger.getLogger(javaClass.name)

    override fun <T : Any> unwrap(iface: Class<T>): T {
        if (iface.isInstance(this)) {
            return iface.cast(this)
        }
        throw SQLException("This data source does not wrap the requested type.")
    }

    override fun isWrapperFor(iface: Class<*>): Boolean = iface.isInstance(this)

    private fun readToken(path: Path): String {
        val bytes =
            try {
                // Follow projected-volume symlinks, but refuse directories and special files.
                if (!Files.isRegularFile(path)) {
                    throw IOException()
                }
                Files.newInputStream(path).use { it.readNBytes(MAX_TOKEN_BYTES + 1) }
            } catch (_: IOException) {
                throw SQLException(
                    "Cannot read the OIDC token file. Mount a readable projected service-account " +
                        "token into the destination connector container.",
                    "28000"
                )
            } catch (_: SecurityException) {
                throw SQLException("Access to the OIDC token file was denied.", "28000")
            }
        if (bytes.size > MAX_TOKEN_BYTES) {
            throw SQLException("The OIDC token file exceeds the 64 KiB limit.", "28000")
        }
        val token = bytes.toString(StandardCharsets.UTF_8).trim()
        if (!JWT_PATTERN.matches(token)) {
            // Do not echo bytes, token contents, or a parsing exception into Airbyte logs.
            throw SQLException(
                "The OIDC token file must contain one non-empty compact JWT.",
                "28000"
            )
        }
        // Snowflake, not this connector, validates signatures, issuer, subject, audience and
        // expiry.
        return token
    }

    companion object {
        private const val MAX_TOKEN_BYTES = 64 * 1024
        private val JWT_PATTERN = Regex("[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+")
        private val AUTHENTICATION_PROPERTIES =
            setOf(
                "authenticator",
                "workloadidentityprovider",
                "token",
                "tokenfilepath",
                "password",
                "privatekey",
                "privatekeyfile",
                "privatekeybase64",
                "privatekeypwd",
                "privatekeyfilepwd",
                "privatekeypassword",
                "oauthclientsecret",
                "passcode",
                "passcodeinpassword",
                "idtokenpassword",
                "oktausername",
            )
        private val URL_IDENTITY_PROPERTIES =
            setOf("user", "username", "account", "workloadidentityentraresource")
        private val ENDPOINT_PROPERTIES =
            setOf("host", "server", "serverurl", "port", "protocol", "scheme")
        // Match on a label boundary, never a substring or an arbitrary top-level domain.
        private val SNOWFLAKE_HOST_SUFFIXES =
            setOf("snowflakecomputing.com", "snowflakecomputing.cn", "snowflakecomputing.mil")
        private val AUTHORITY_PATTERN = Regex("([A-Za-z0-9_.-]+)(?::([0-9]{1,5}))?")
        private val HOST_LABEL_PATTERN = Regex("[A-Za-z0-9_](?:[A-Za-z0-9_-]{0,61}[A-Za-z0-9_])?")

        private fun normalizeProperty(value: String): String {
            // JDBC compares names with equalsIgnoreCase and uppercases them. Unicode case
            // folding differs from lowercase(), so reject non-ASCII names before normalization.
            // This applies to decoded URL keys and Properties, including inherited defaults.
            require(value.all { it.code <= 0x7F }) {
                "Workload identity JDBC property names must contain only ASCII characters."
            }
            return value.lowercase(Locale.ROOT).replace("_", "").replace("-", "").trim()
        }

        private fun validateTokenPath(
            provider: WorkloadIdentityProvider,
            tokenFilePath: String?,
        ): Path? {
            if (provider != WorkloadIdentityProvider.OIDC) {
                require(tokenFilePath.isNullOrBlank()) {
                    "token_file_path is only supported with the OIDC workload identity provider."
                }
                return null
            }
            require(!tokenFilePath.isNullOrBlank()) {
                "token_file_path is required with the OIDC workload identity provider."
            }
            val path =
                try {
                    Path.of(tokenFilePath)
                } catch (_: InvalidPathException) {
                    throw IllegalArgumentException("token_file_path must be a valid absolute path.")
                }
            require(path.isAbsolute) { "token_file_path must be an absolute path." }
            // No file I/O during construction, schema generation, or configuration deserialization.
            return path
        }

        private fun validateSsl(name: String, value: String) {
            // JDBC 3.26.1 recognizes both false and off, including in Properties and duplicate
            // URL parameters. Validate every occurrence; setting ssl=true later does not undo HTTP.
            require(name != "ssl" || value.equals("true", ignoreCase = true)) {
                "Workload identity federation requires HTTPS; ssl must be true when specified."
            }
        }

        private fun validateJdbcUrl(jdbcUrl: String) {
            val uri =
                try {
                    require(jdbcUrl.startsWith("jdbc:snowflake://"))
                    val endpoint = jdbcUrl.removePrefix("jdbc:snowflake://")
                    // The pinned driver supports an explicit scheme after its JDBC prefix.
                    URI(
                        if (endpoint.startsWith("https://") || endpoint.startsWith("http://")) {
                            endpoint
                        } else {
                            "snowflake://$endpoint"
                        }
                    )
                } catch (_: Exception) {
                    throw IllegalArgumentException(
                        "Invalid Snowflake JDBC URL for workload identity."
                    )
                }
            require(uri.scheme == "snowflake" || uri.scheme == "https") {
                "Workload identity federation requires HTTPS."
            }
            require(
                uri.rawUserInfo == null &&
                    uri.rawFragment == null &&
                    (uri.rawPath.isNullOrEmpty() || uri.rawPath == "/")
            ) {
                "The workload identity JDBC URL must not contain user-info, a fragment, or a path."
            }

            // URI.host is null for legitimate Snowflake account names containing underscores.
            // Validate the entire raw authority instead. This also rejects percent encoding,
            // user-info, IP literals, backslashes, and ambiguous or invalid ports.
            val authority =
                AUTHORITY_PATTERN.matchEntire(uri.rawAuthority.orEmpty())
                    ?: throw IllegalArgumentException("Invalid workload identity JDBC authority.")
            val host = authority.groupValues[1].lowercase(Locale.ROOT)
            val port = authority.groupValues[2]
            require(port.isEmpty() || port.toInt() in 1..65535) {
                "Invalid workload identity JDBC port."
            }
            require(
                host.length <= 253 &&
                    host.split('.').all { HOST_LABEL_PATTERN.matches(it) } &&
                    SNOWFLAKE_HOST_SUFFIXES.any { host.endsWith(".$it") }
            ) { "Workload identity federation requires a recognized Snowflake hostname." }

            uri.rawQuery
                .orEmpty()
                .split('&', ';')
                .filter { it.isNotBlank() }
                .forEach { parameter ->
                    val decodedName: String
                    val value: String
                    try {
                        decodedName =
                            URLDecoder.decode(
                                parameter.substringBefore('='),
                                StandardCharsets.UTF_8
                            )
                        value =
                            URLDecoder.decode(
                                parameter.substringAfter('=', ""),
                                StandardCharsets.UTF_8
                            )
                    } catch (_: IllegalArgumentException) {
                        throw IllegalArgumentException("Invalid encoding in JDBC URL parameters.")
                    }
                    val name = normalizeProperty(decodedName)
                    require(
                        name !in AUTHENTICATION_PROPERTIES &&
                            name !in URL_IDENTITY_PROPERTIES &&
                            name !in ENDPOINT_PROPERTIES
                    ) {
                        "Do not set authentication, identity, or endpoint overrides in jdbc_url_params when " +
                            "using workload identity federation."
                    }
                    validateSsl(name, value)
                }
        }
    }
}
