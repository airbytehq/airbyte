/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.auth

import java.io.PrintWriter
import java.io.StringWriter
import java.lang.reflect.Proxy
import java.net.URLEncoder
import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.StandardCopyOption
import java.sql.Connection
import java.sql.Driver
import java.sql.DriverPropertyInfo
import java.sql.SQLException
import java.sql.SQLFeatureNotSupportedException
import java.util.Collections
import java.util.IdentityHashMap
import java.util.Properties
import java.util.concurrent.Callable
import java.util.concurrent.CopyOnWriteArrayList
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.logging.Logger
import javax.sql.DataSource

/**
 * Shared by the JUnit test factory and the dependency-free command-line regression runner. No real
 * tokens, Snowflake account, network access, or cloud credentials are needed.
 */
internal object SnowflakeWorkloadIdentityScenarios {
    private const val URL = "jdbc:snowflake://example.snowflakecomputing.com/"
    private const val TOKEN_ONE = "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJvbmUifQ.signature_one"
    private const val TOKEN_TWO = "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ0d28ifQ.signature_two"

    fun cases(): List<Pair<String, () -> Unit>> = buildList {
        add(
            "OIDC reads a fresh token on every connection without retaining it" to
                {
                    withDirectory { directory ->
                        val path = Files.writeString(directory.resolve("token"), "$TOKEN_ONE\n")
                        val properties = Properties().apply { setProperty("user", "AIRBYTE_USER") }
                        val driver = RecordingDriver()
                        val source =
                            source(
                                driver,
                                WorkloadIdentityProvider.OIDC,
                                path.toString(),
                                properties
                            )
                        source.connection.close()
                        Files.writeString(path, TOKEN_TWO)
                        source.connection.close()
                        check(
                            driver.calls.map { it.getProperty("token") } ==
                                listOf(TOKEN_ONE, TOKEN_TWO)
                        )
                        check(driver.calls.all { it.getProperty("user") == "AIRBYTE_USER" })
                        check(properties.getProperty("token") == null)
                        check(driver.calls[0] !== driver.calls[1])
                        check(
                            driver.calls.all {
                                it.getProperty("authenticator") == "WORKLOAD_IDENTITY"
                            }
                        )
                        check(
                            driver.calls.all {
                                it.getProperty("workloadIdentityProvider") == "OIDC"
                            }
                        )
                    }
                }
        )
        add(
            "follows an atomically rotated Kubernetes projected volume" to
                {
                    withDirectory { directory ->
                        val first = Files.createDirectory(directory.resolve("generation-1"))
                        val second = Files.createDirectory(directory.resolve("generation-2"))
                        Files.writeString(first.resolve("token"), TOKEN_ONE)
                        Files.writeString(second.resolve("token"), TOKEN_TWO)
                        Files.createSymbolicLink(directory.resolve("..data"), first.fileName)
                        val token =
                            Files.createSymbolicLink(
                                directory.resolve("token"),
                                Path.of("..data/token")
                            )
                        val driver = RecordingDriver()
                        val source = source(driver, WorkloadIdentityProvider.OIDC, token.toString())
                        source.connection.close()
                        Files.createSymbolicLink(directory.resolve("..data-next"), second.fileName)
                        Files.move(
                            directory.resolve("..data-next"),
                            directory.resolve("..data"),
                            StandardCopyOption.ATOMIC_MOVE,
                            StandardCopyOption.REPLACE_EXISTING,
                        )
                        source.connection.close()
                        check(
                            driver.calls.map { it.getProperty("token") } ==
                                listOf(TOKEN_ONE, TOKEN_TWO)
                        )
                    }
                }
        )
        add(
            "does not read the file at construction and fails safely at login" to
                {
                    withDirectory { directory ->
                        val driver = RecordingDriver()
                        val source =
                            source(
                                driver,
                                WorkloadIdentityProvider.OIDC,
                                directory.resolve("missing").toString()
                            )
                        check(driver.calls.isEmpty())
                        val error = expect<SQLException> { source.connection }
                        check(error.sqlState == "28000" && error.cause == null)
                        check(driver.calls.isEmpty())
                    }
                }
        )
        add(
            "does not reuse the previous token after the file disappears" to
                {
                    withDirectory { directory ->
                        val path = Files.writeString(directory.resolve("token"), TOKEN_ONE)
                        val driver = RecordingDriver()
                        val source = source(driver, WorkloadIdentityProvider.OIDC, path.toString())
                        source.connection.close()
                        Files.delete(path)
                        expect<SQLException> { source.connection }
                        check(driver.calls.size == 1)
                    }
                }
        )
        listOf(
                "",
                " \n\t",
                "private-secret-material",
                "$TOKEN_ONE\n$TOKEN_TWO",
                "a.b.",
                "a..c",
                "a.b.c.d"
            )
            .forEachIndexed { index, contents ->
                add(
                    "rejects invalid token contents $index without exposing them" to
                        {
                            withDirectory { directory ->
                                val path = Files.writeString(directory.resolve("token"), contents)
                                val driver = RecordingDriver()
                                val error =
                                    expect<SQLException> {
                                        source(
                                                driver,
                                                WorkloadIdentityProvider.OIDC,
                                                path.toString()
                                            )
                                            .connection
                                    }
                                check(error.sqlState == "28000" && error.cause == null)
                                check(!error.message.orEmpty().contains("private-secret-material"))
                                check(!error.message.orEmpty().contains(TOKEN_ONE))
                                check(driver.calls.isEmpty())
                            }
                        }
                )
            }
        add(
            "rejects oversized files before calling the driver" to
                {
                    withDirectory { directory ->
                        val path =
                            Files.writeString(
                                directory.resolve("token"),
                                "a.b." + "c".repeat(65536)
                            )
                        val driver = RecordingDriver()
                        val error =
                            expect<SQLException> {
                                source(driver, WorkloadIdentityProvider.OIDC, path.toString())
                                    .connection
                            }
                        check(error.message.orEmpty().contains("64 KiB"))
                        check(driver.calls.isEmpty())
                    }
                }
        )
        add(
            "rejects directories in place of tokens" to
                {
                    withDirectory { directory ->
                        expect<SQLException> {
                            source(
                                    RecordingDriver(),
                                    WorkloadIdentityProvider.OIDC,
                                    directory.toString()
                                )
                                .connection
                        }
                    }
                }
        )
        listOf<String?>(null, "", " ", "relative/token", "/invalid\u0000path").forEachIndexed {
            index,
            path ->
            add(
                "rejects invalid OIDC token path $index at construction" to
                    {
                        expect<IllegalArgumentException> {
                            source(RecordingDriver(), WorkloadIdentityProvider.OIDC, path)
                        }
                    }
            )
        }
        listOf(
                WorkloadIdentityProvider.AWS,
                WorkloadIdentityProvider.AZURE,
                WorkloadIdentityProvider.GCP
            )
            .forEach { provider ->
                add(
                    "$provider delegates attestation to the driver without a token" to
                        {
                            val driver = RecordingDriver()
                            val source = source(driver, provider)
                            source.connection.close()
                            source.connection.close()
                            check(driver.calls.size == 2)
                            check(
                                driver.calls.all {
                                    it.getProperty("authenticator") == "WORKLOAD_IDENTITY"
                                }
                            )
                            check(
                                driver.calls.all {
                                    it.getProperty("workloadIdentityProvider") == provider.name
                                }
                            )
                            check(
                                driver.calls.all {
                                    it.getProperty("token") == null &&
                                        it.getProperty("password") == null
                                }
                            )
                            expect<IllegalArgumentException> {
                                source(driver, provider, "/unwanted/token")
                            }
                        }
                )
            }
        add(
            "preserves typed session properties and defensively copies defaults" to
                {
                    val defaults = Properties().apply { setProperty("role", "AIRBYTE_ROLE") }
                    val properties =
                        Properties(defaults).apply {
                            setProperty("warehouse", "AIRBYTE_WH")
                            put("MULTI_STATEMENT_COUNT", 0)
                            setProperty("workloadIdentityEntraResource", "api://example-resource")
                        }
                    val driver = RecordingDriver()
                    val source =
                        source(driver, WorkloadIdentityProvider.AZURE, properties = properties)
                    properties.setProperty("warehouse", "changed")
                    defaults.setProperty("role", "changed")
                    source.connection.close()
                    check(driver.calls.single().getProperty("warehouse") == "AIRBYTE_WH")
                    check(driver.calls.single().getProperty("role") == "AIRBYTE_ROLE")
                    check(driver.calls.single()["MULTI_STATEMENT_COUNT"] == 0)
                    check(
                        driver.calls.single().getProperty("workloadIdentityEntraResource") ==
                            "api://example-resource"
                    )
                    driver.calls.single().setProperty("warehouse", "driver-mutated")
                    source.connection.close()
                    check(driver.calls.last().getProperty("warehouse") == "AIRBYTE_WH")
                }
        )
        add(
            "concurrent connections use isolated property objects" to
                {
                    withDirectory { directory ->
                        val path = Files.writeString(directory.resolve("token"), TOKEN_ONE)
                        val driver = RecordingDriver()
                        val source = source(driver, WorkloadIdentityProvider.OIDC, path.toString())
                        val executor = Executors.newFixedThreadPool(8)
                        try {
                            executor
                                .invokeAll((1..32).map { Callable { source.connection.close() } })
                                .forEach { it.get(10, TimeUnit.SECONDS) }
                        } finally {
                            executor.shutdownNow()
                        }
                        val identities =
                            Collections.newSetFromMap(IdentityHashMap<Properties, Boolean>())
                        identities.addAll(driver.calls)
                        check(identities.size == 32)
                        check(driver.calls.all { it.getProperty("token") == TOKEN_ONE })
                    }
                }
        )
        listOf(
                "token",
                "TOKEN",
                "authenticator",
                "workload_identity_provider",
                "private_key_file",
                "privateKey",
                "password"
            )
            .forEach { key ->
                add(
                    "rejects the conflicting base property $key" to
                        {
                            expect<IllegalArgumentException> {
                                source(
                                    RecordingDriver(),
                                    properties =
                                        Properties().apply {
                                            setProperty(key, "private-secret-material")
                                        }
                                )
                            }
                        }
                )
            }
        add(
            "rejects credentials hidden in Properties defaults" to
                {
                    val defaults =
                        Properties().apply { setProperty("password", "private-secret-material") }
                    expect<IllegalArgumentException> {
                        source(RecordingDriver(), properties = Properties(defaults))
                    }
                }
        )
        listOf(
                "authenticator=oauth",
                "AUTHENTICATOR=oauth",
                "%61uthenticator=oauth",
                "role=A;token=private-secret-material",
                "role=A&token=private-secret-material",
                "workloadIdentityProvider=AWS",
                "workload_identity_provider=AWS",
                "token_file_path=/tmp/token",
                "private_key_file=/tmp/key",
                "privateKey=secret",
                "PASSWORD=secret",
                "user=other",
                "username=other",
                "account=other",
                "serverURL=other",
                "workloadIdentityEntraResource=other",
            )
            .forEachIndexed { index, query ->
                add(
                    "rejects JDBC URL authentication or identity override $index" to
                        {
                            val error =
                                expect<IllegalArgumentException> {
                                    source(RecordingDriver(), url = "$URL?$query")
                                }
                            check(!error.message.orEmpty().contains("private-secret-material"))
                        }
                )
            }
        listOf(
                "jdbc:other://example/",
                "jdbc:snowflake://user:secret@example.com/",
                "$URL#fragment",
                "$URL?x=%broken"
            )
            .forEachIndexed { index, url ->
                add(
                    "rejects malformed or ambiguous JDBC URL $index" to
                        {
                            expect<IllegalArgumentException> {
                                source(RecordingDriver(), url = url)
                            }
                        }
                )
            }
        val unsafeUrls =
            listOf(
                "jdbc:snowflake://http://example.snowflakecomputing.com/",
                "jdbc:snowflake://http://example.snowflakecomputing.com/?ssl=true",
                "$URL?ssl=false",
                "$URL?SSL=OFF",
                "$URL?%73sl=%66alse",
                "$URL?ssl=false&ssl=true",
                "$URL?ssl=true&ssl=off",
                "$URL?ssl=",
                "$URL?ssl",
                "$URL?ssl=0",
                "$URL?host=never-log-this.invalid",
                "$URL?serverURL=https%3A%2F%2Fnever-log-this.invalid",
                "$URL?protocol=http",
                "$URL?port=80",
                "jdbc:snowflake://never-log-this.invalid/",
                "jdbc:snowflake://example.snowflakecomputing.com.never-log-this.invalid/",
                "jdbc:snowflake://notsnowflakecomputing.com/",
                "jdbc:snowflake://example.privatelink.snowflakecomputing.invalid/",
                "jdbc:snowflake://snowflakecomputing.com/",
                "jdbc:snowflake://example.localstack.cloud/",
                "jdbc:snowflake://127.0.0.1/",
                "jdbc:snowflake://[::1]/",
                "jdbc:snowflake://example.snowflakecomputing.com@never-log-this.invalid/",
                "jdbc:snowflake://never-log-this@example.snowflakecomputing.com/",
                "jdbc:snowflake://example%2Esnowflakecomputing.com/",
                "jdbc:snowflake://example.snowflakecomputing.com:0/",
                "jdbc:snowflake://example.snowflakecomputing.com:65536/",
                "jdbc:snowflake://example.snowflakecomputing.com:443:80/",
                "jdbc:snowflake://example.snowflakecomputing.com:/",
                "jdbc:snowflake://example.snowflakecomputing.com/never-log-this",
                "jdbc:snowflake://example..snowflakecomputing.com/",
                "jdbc:snowflake://-example.snowflakecomputing.com/",
                "jdbc:snowflake://example-.snowflakecomputing.com/",
                "jdbc:snowflake://example.snowflakecomputing.com./",
                "jdbc:snowflake://https://example.snowflakecomputing.com/?ssl=off",
            )
        WorkloadIdentityProvider.values().forEach { provider ->
            unsafeUrls.forEachIndexed { index, url ->
                add(
                    "$provider rejects unsafe endpoint $index before credential acquisition" to
                        {
                            val driver = RecordingDriver()
                            val path =
                                if (provider == WorkloadIdentityProvider.OIDC)
                                    "/not-mounted-yet/token"
                                else null
                            val error =
                                expect<IllegalArgumentException> {
                                    source(driver, provider, path, url = url)
                                }
                            check(driver.calls.isEmpty())
                            check(!error.message.orEmpty().contains("never-log-this"))
                        }
                )
            }
        }
        listOf(
                "jdbc:snowflake://example.snowflakecomputing.com",
                "jdbc:snowflake://orgname-account_name.snowflakecomputing.com/?",
                "jdbc:snowflake://orgname-account_name.privatelink.snowflakecomputing.com/",
                "jdbc:snowflake://ACCOUNT.us-east-1.aws.snowflakecomputing.COM/",
                "jdbc:snowflake://account.snowflakecomputing.cn/",
                "jdbc:snowflake://account.snowflakecomputing.mil:443/",
                "jdbc:snowflake://https://orgname-account_name.snowflakecomputing.com/",
                "$URL?ssl=true",
                "$URL?%73sl=%74rue",
                "$URL?ssl=TRUE&ssl=true&loginTimeout=30",
            )
            .forEachIndexed { index, url ->
                add(
                    "accepts trusted HTTPS endpoint $index without rewriting account underscores" to
                        {
                            val driver = RecordingDriver()
                            source(driver, url = url).connection.close()
                            check(driver.urls.single() == url)
                        }
                )
            }
        listOf(
                "ssl" to "false",
                "SSL" to "OFF",
                "ssl" to "",
                "serverURL" to "https://never-log-this.invalid",
                "host" to "never-log-this.invalid",
                "protocol" to "http",
                "port" to "80"
            )
            .forEach { (name, value) ->
                listOf(false, true).forEach { defaults ->
                    add(
                        "rejects unsafe $name in JDBC Properties (defaults=$defaults)" to
                            {
                                val properties = Properties().apply { setProperty(name, value) }
                                val driver = RecordingDriver()
                                expect<IllegalArgumentException> {
                                    source(
                                        driver,
                                        properties =
                                            if (defaults) Properties(properties) else properties
                                    )
                                }
                                check(driver.calls.isEmpty())
                            }
                    )
                }
            }
        add(
            "accepts boolean ssl true and rejects boolean ssl false in JDBC Properties" to
                {
                    source(RecordingDriver(), properties = Properties().apply { put("ssl", true) })
                        .connection
                        .close()
                    expect<IllegalArgumentException> {
                        source(
                            RecordingDriver(),
                            properties = Properties().apply { put("ssl", false) }
                        )
                    }
                }
        )
        // Long s is equal to ASCII s under JDBC's equalsIgnoreCase; Kelvin sign also verifies
        // that non-ASCII names are rejected before lowercase() could turn them into ASCII.
        listOf(
                "\u017Fsl",
                "s\u017Fl",
                "\u017F\u017Fl",
                "authent\u0131cator",
                "\u212Aey",
                "caf\u00E9"
            )
            .forEachIndexed { index, name ->
                listOf("raw URL", "encoded URL", "Properties", "Properties defaults").forEach {
                    input ->
                    add(
                        "rejects non-ASCII property name $index from $input for every provider" to
                            {
                                WorkloadIdentityProvider.values().forEach { provider ->
                                    val properties =
                                        Properties().apply { setProperty("ssl", "true") }
                                    val encodedName =
                                        URLEncoder.encode(name, StandardCharsets.UTF_8)
                                    val url =
                                        when (input) {
                                            "raw URL" -> "$URL?$name=false&ssl=true"
                                            "encoded URL" -> "$URL?$encodedName=false&ssl=true"
                                            else -> URL
                                        }
                                    if (input.startsWith("Properties")) {
                                        properties.setProperty(name, "false")
                                    }
                                    val driver = RecordingDriver()
                                    val error =
                                        expect<IllegalArgumentException> {
                                            source(
                                                driver,
                                                provider,
                                                if (provider == WorkloadIdentityProvider.OIDC)
                                                    "/not-mounted-yet/token"
                                                else null,
                                                if (input == "Properties defaults")
                                                    Properties(properties)
                                                else properties,
                                                url,
                                            )
                                        }
                                    check(error.message.orEmpty().contains("ASCII"))
                                    check(!error.message.orEmpty().contains(name))
                                    check(driver.calls.isEmpty())
                                }
                            }
                    )
                }
            }
        add(
            "permits Unicode property values with ASCII names" to
                {
                    val value = "caf\u00E9-\u65E5\u672C"
                    val properties = Properties().apply { setProperty("query_tag", value) }
                    val url = "$URL?query_tag=${URLEncoder.encode(value, StandardCharsets.UTF_8)}"
                    val driver = RecordingDriver()
                    source(driver, properties = properties, url = url).connection.close()
                    check(driver.calls.single().getProperty("query_tag") == value)
                    check(driver.urls.single() == url)
                }
        )
        add(
            "passes benign JDBC URL parameters through unchanged" to
                {
                    val driver = RecordingDriver()
                    val url = "$URL?loginTimeout=30&query_tag=some%20job"
                    source(driver, url = url).connection.close()
                    check(driver.urls.single() == url)
                }
        )
        add(
            "refuses password overrides but supports Hikari's null overload" to
                {
                    val driver = RecordingDriver()
                    val source = source(driver)
                    expect<SQLFeatureNotSupportedException> {
                        source.getConnection("user", "password")
                    }
                    expect<SQLFeatureNotSupportedException> { source.getConnection("", null) }
                    check(driver.calls.isEmpty())
                    source.getConnection(null, null).close()
                    check(driver.calls.size == 1)
                }
        )
        add(
            "supports login timeout and wrapper contracts without logging secrets" to
                {
                    val driver = RecordingDriver()
                    val source = source(driver)
                    check(source.loginTimeout == 0)
                    expect<SQLException> { source.loginTimeout = -1 }
                    source.loginTimeout = 19
                    source.connection.close()
                    check(driver.calls.single().getProperty("loginTimeout") == "19")
                    check(source.loginTimeout == 19)
                    check(source.isWrapperFor(DataSource::class.java))
                    check(source.unwrap(DataSource::class.java) === source)
                    check(!source.isWrapperFor(Connection::class.java))
                    expect<SQLException> { source.unwrap(Connection::class.java) }
                    val output = StringWriter()
                    val writer = PrintWriter(output)
                    source.logWriter = writer
                    source.connection.close()
                    check(source.logWriter === writer && output.toString().isEmpty())
                    check(source.parentLogger.name == source.javaClass.name)
                }
        )
        add(
            "reports driver rejection with a connection SQLSTATE" to
                {
                    val error =
                        expect<SQLException> { source(RecordingDriver(reject = true)).connection }
                    check(error.sqlState == "08001")
                }
        )
    }

    @JvmStatic
    fun main(args: Array<String>) {
        val cases = cases()
        cases.forEach { (name, run) ->
            run()
            println("PASS: $name")
        }
        println("${cases.size} workload identity regression scenarios passed")
    }

    private fun source(
        driver: Driver,
        provider: WorkloadIdentityProvider = WorkloadIdentityProvider.AWS,
        path: String? = null,
        properties: Properties = Properties(),
        url: String = URL,
    ) = SnowflakeWorkloadIdentityDataSource(url, properties, provider, path, driver)

    private inline fun <reified T : Throwable> expect(block: () -> Unit): T {
        try {
            block()
        } catch (error: Throwable) {
            check(error is T) { "Expected ${T::class.java.name}, got ${error.javaClass.name}" }
            return error
        }
        error("Expected ${T::class.java.name}")
    }

    private inline fun withDirectory(block: (Path) -> Unit) {
        val directory = Files.createTempDirectory("snowflake-wif-test-")
        try {
            block(directory)
        } finally {
            // Files.walk does not follow symlinks, including the projected-volume test links.
            Files.walk(directory).use { paths ->
                paths.sorted(Comparator.reverseOrder()).forEach { Files.deleteIfExists(it) }
            }
        }
    }

    private class RecordingDriver(private val reject: Boolean = false) : Driver {
        val calls = CopyOnWriteArrayList<Properties>()
        val urls = CopyOnWriteArrayList<String>()

        override fun connect(url: String, info: Properties): Connection? {
            urls.add(url)
            calls.add(info)
            if (reject) return null
            return Proxy.newProxyInstance(
                Connection::class.java.classLoader,
                arrayOf(Connection::class.java)
            ) { _, method, _ ->
                when (method.name) {
                    "close" -> null
                    "isClosed" -> false
                    else -> throw UnsupportedOperationException(method.name)
                }
            } as Connection
        }

        override fun acceptsURL(url: String): Boolean = url.startsWith("jdbc:snowflake://")
        override fun getPropertyInfo(url: String?, info: Properties?): Array<DriverPropertyInfo> =
            emptyArray()
        override fun getMajorVersion(): Int = 1
        override fun getMinorVersion(): Int = 0
        override fun jdbcCompliant(): Boolean = false
        override fun getParentLogger(): Logger = Logger.getLogger(javaClass.name)
    }
}
