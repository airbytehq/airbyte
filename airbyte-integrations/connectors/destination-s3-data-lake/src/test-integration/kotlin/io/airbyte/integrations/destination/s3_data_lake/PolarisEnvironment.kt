/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import java.io.File
import java.lang.ProcessBuilder
import java.net.URI
import java.net.URLEncoder
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.time.Duration
import java.util.Base64
import java.util.concurrent.atomic.AtomicBoolean

/**
 * WARNING: This file is tightly coupled with docker-compose.yml. Any changes to service
 * configurations in docker-compose.yml (ports, credentials, service names, bootstrap credentials,
 * etc.) must be reflected in the constants below and vice versa. See:
 * src/test-integration/resources/polaris/docker-compose.yml
 */
object PolarisEnvironment {

    private val composeFile = File("src/test-integration/resources/polaris/docker-compose.yml")
    private val startedOnce = AtomicBoolean(false)

    private const val MINIO = "http://localhost:9000"
    private const val POLARIS_REST_BASE = "http://localhost:8181/api"
    private const val POLARIS_MGMT_BASE = "http://localhost:8181/api/management/v1"
    private const val OAUTH_TOKEN_URL = "http://localhost:8181/api/catalog/v1/oauth/tokens"

    private const val POLARIS_HEALTH_PRIMARY = "http://localhost:8182/q/health/ready"
    private const val POLARIS_HEALTH_FALLBACK = "http://localhost:8182/health/ready"

    private const val REALM_HEADER_NAME = "Polaris-Realm"
    private const val REALM = "POLARIS"
    private const val BOOTSTRAP_ID = "root"
    private const val BOOTSTRAP_SECRET = "s3cr3t"

    private const val CATALOG_NAME = "quickstart_catalog"
    private const val PRINCIPAL_BASENAME = "quickstart_user"
    private const val PRINCIPAL_ROLE = "quickstart_user_role"
    private const val CATALOG_ROLE = "quickstart_catalog_role"
    private const val BUCKET = "bucket123"

    @Volatile private var appClientId: String? = null
    @Volatile private var appClientSecret: String? = null

    @Volatile private var bearerToken: String? = null

    private val http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).build()

    /**
     * Starts the Polaris environment using docker-compose. This includes MinIO (S3-compatible
     * storage), PostgreSQL (metadata store), and Polaris (catalog service). After starting
     * services, it creates the catalog and sets up authentication with proper privileges. This
     * method is idempotent - it will only start services once per JVM instance.
     */
    fun startServices() {
        if (startedOnce.compareAndSet(false, true)) {
            val up =
                ProcessBuilder(
                        "docker",
                        "compose",
                        "-f",
                        composeFile.absolutePath,
                        "up",
                        "-d",
                    )
                    .inheritIO()
                    .start()
            val exitCode = up.waitFor()
            if (exitCode != 0)
                error("Failed to start docker-compose services. Exit code: $exitCode")

            waitFor("$MINIO/minio/health/ready", timeoutSec = 120)

            if (
                !waitForOrFalse(POLARIS_HEALTH_PRIMARY, 150) &&
                    !waitForOrFalse(POLARIS_HEALTH_FALLBACK, 60)
            ) {
                error(
                    "Polaris health endpoint not ready on $POLARIS_HEALTH_PRIMARY nor $POLARIS_HEALTH_FALLBACK"
                )
            }

            requireApiReady()

            createCatalogIfNeeded()
            createPrincipalAndGrants()
        }
    }

    /**
     * Returns the JSON configuration for the S3 Data Lake connector. This configuration includes
     * Polaris catalog settings, S3 storage credentials, and OAuth credentials (Client ID and Client
     * Secret) for authenticating with Polaris. Automatically starts services if not already
     * running.
     */
    fun getConfig(): String {
        startServices()

        val credential = "${requireNotNull(appClientId)}:${requireNotNull(appClientSecret)}"
        val serverUri = "$POLARIS_REST_BASE/catalog"
        val s3Endpoint = MINIO

        return """
      {
        "catalog_type": {
          "catalog_type": "POLARIS",
          "server_uri": "$serverUri",
          "catalog_name": "$CATALOG_NAME",
          "client_id": "$appClientId",
          "client_secret": "$appClientSecret",
          "namespace": "<DEFAULT_NAMESPACE_PLACEHOLDER>"
        },
        "s3_bucket_name": "$BUCKET",
        "s3_bucket_region": "us-east-1",
        "access_key_id": "minio_root",
        "secret_access_key": "m1n1opwd",
        "s3_endpoint": "$s3Endpoint",
        "warehouse_location": "s3://$BUCKET/",
        "main_branch_name": "main"
      }
    """.trimIndent()
    }

    /**
     * Stops all docker-compose services and clears cached credentials. This method removes all
     * containers and volumes created by docker-compose.
     */
    fun stopServices() {
        if (startedOnce.compareAndSet(true, false)) {
            ProcessBuilder(
                    "docker",
                    "compose",
                    "-f",
                    composeFile.absolutePath,
                    "down",
                    "-v",
                )
                .inheritIO()
                .start()
                .waitFor()
            bearerToken = null
            appClientId = null
            appClientSecret = null
        }
    }

    /**
     * Polls the given URL until it returns a 2xx status code or times out. Throws
     * IllegalStateException if the endpoint doesn't become ready within the timeout period.
     */
    private fun waitFor(url: String, timeoutSec: Int) {
        val deadline = System.nanoTime() + Duration.ofSeconds(timeoutSec.toLong()).toNanos()
        var lastErr: Throwable? = null
        while (System.nanoTime() < deadline) {
            try {
                val req =
                    HttpRequest.newBuilder(URI.create(url))
                        .timeout(Duration.ofSeconds(3))
                        .GET()
                        .build()
                val res = http.send(req, HttpResponse.BodyHandlers.discarding())
                if (res.statusCode() in 200..299) return
                lastErr = RuntimeException("HTTP ${res.statusCode()}")
            } catch (t: Throwable) {
                lastErr = t
            }
            Thread.sleep(500)
        }
        throw IllegalStateException("Timeout waiting for $url", lastErr)
    }

    /**
     * Similar to waitFor but returns false instead of throwing an exception on timeout. Used for
     * checking fallback health endpoints.
     */
    private fun waitForOrFalse(url: String, timeoutSec: Int): Boolean =
        try {
            waitFor(url, timeoutSec)
            true
        } catch (_: Throwable) {
            false
        }

    /**
     * Fetches an OAuth bearer token using the bootstrap credentials. Uses OAuth 2.0 client
     * credentials flow with the root principal.
     */
    private fun fetchToken(scope: String = "PRINCIPAL_ROLE:ALL"): String {
        val form = "grant_type=client_credentials&scope=${URLEncoder.encode(scope, Charsets.UTF_8)}"
        val req =
            HttpRequest.newBuilder(URI.create(OAUTH_TOKEN_URL))
                .timeout(Duration.ofSeconds(15))
                .header(REALM_HEADER_NAME, REALM)
                .header("Authorization", adminBasicAuthHeader())
                .header("Content-Type", "application/x-www-form-urlencoded")
                .POST(HttpRequest.BodyPublishers.ofString(form))
                .build()
        val res = http.send(req, HttpResponse.BodyHandlers.ofString())
        if (res.statusCode() !in 200..299) {
            error("Token request failed: ${res.statusCode()} ${res.body()}")
        }
        val token =
            "\"access_token\"\\s*:\\s*\"([^\"]+)\"".toRegex().find(res.body())?.groupValues?.get(1)
        require(!token.isNullOrBlank()) { "No access_token in response: ${res.body()}" }
        return token!!
    }

    /** Generates HTTP Basic Authentication header using the bootstrap credentials. */
    private fun adminBasicAuthHeader(): String {
        val token = "$BOOTSTRAP_ID:$BOOTSTRAP_SECRET"
        val b64 = Base64.getEncoder().encodeToString(token.toByteArray())
        return "Basic $b64"
    }

    /**
     * Sends an HTTP request with automatic token refresh on 401 responses. If the request fails
     * with 401 Unauthorized, it fetches a new token and retries once.
     */
    private fun sendWithAutoRefresh(build: (String) -> HttpRequest): HttpResponse<String> {
        var token = bearerToken ?: fetchToken().also { bearerToken = it }
        var req = build(token)
        var res = http.send(req, HttpResponse.BodyHandlers.ofString())
        if (res.statusCode() == 401) {
            bearerToken = null
            token = fetchToken().also { bearerToken = it }
            req = build(token)
            res = http.send(req, HttpResponse.BodyHandlers.ofString())
        }
        return res
    }

    /**
     * Verifies that the Polaris Management API is ready to accept requests. Throws an error if the
     * API is not accessible.
     */
    private fun requireApiReady() {
        val res = sendWithAutoRefresh { token ->
            HttpRequest.newBuilder(URI.create("$POLARIS_MGMT_BASE/catalogs"))
                .timeout(Duration.ofSeconds(10))
                .header(REALM_HEADER_NAME, REALM)
                .header("Authorization", "Bearer $token")
                .GET()
                .build()
        }
        if (res.statusCode() !in 200..299) {
            error("Polaris Management API not ready: ${res.statusCode()} ${res.body()}")
        }
    }

    /** Sends a POST request to the Polaris Management API with automatic token refresh. */
    private fun postJsonAdmin(path: String, body: String): HttpResponse<String> =
        sendWithAutoRefresh { token ->
            HttpRequest.newBuilder(URI.create("$POLARIS_MGMT_BASE$path"))
                .timeout(Duration.ofSeconds(20))
                .header(REALM_HEADER_NAME, REALM)
                .header("Authorization", "Bearer $token")
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build()
        }

    private fun putJsonAdmin(path: String, body: String): HttpResponse<String> =
        sendWithAutoRefresh { token ->
            HttpRequest.newBuilder(URI.create("$POLARIS_MGMT_BASE$path"))
                .timeout(Duration.ofSeconds(20))
                .header(REALM_HEADER_NAME, REALM)
                .header("Authorization", "Bearer $token")
                .header("Content-Type", "application/json")
                .PUT(HttpRequest.BodyPublishers.ofString(body))
                .build()
        }

    private fun postIgnore409(path: String, body: String) {
        val res = postJsonAdmin(path, body)
        if (res.statusCode() in 200..299 || res.statusCode() == 409) return
        error("POST $path failed: ${res.statusCode()} ${res.body()}")
    }

    /**
     * Creates the Polaris catalog with S3 storage configuration. Uses INTERNAL catalog type, which
     * means Polaris manages the storage configuration. Configures MinIO as the S3-compatible
     * storage backend with path-style access.
     */
    private fun createCatalogIfNeeded() {
        val body =
            """
    {
      "catalog": {
        "type": "INTERNAL",
        "name": "$CATALOG_NAME",
        "properties": {
          "default-base-location": "s3://$BUCKET/"
        },
        "storageConfigInfo": {
          "storageType": "S3",
          "region": "us-east-1",
          "endpoint": "$MINIO",
          "endpointInternal": "http://minio:9000",
          "pathStyleAccess": true,
          "stsUnavailable": true
        }
      }
    }
  """.trimIndent()

        val res = postJsonAdmin("/catalogs", body)
        when (res.statusCode()) {
            in 200..299 -> {
                /* created */
            }
            409 -> {
                /* already exists */
            }
            else -> error("Catalog create failed: ${res.statusCode()} ${res.body()}")
        }
    }

    /**
     * Grants specific granular privileges required by the Airbyte S3 Data Lake connector. This
     * includes table operations (list, create, drop, read/write properties, write data) and
     * namespace operations (list, create, read properties).
     *
     * Alternative: Use grantCatalogManageContentPrivilege() for a single broad privilege.
     */
    private fun grantAirbytePrivileges(catalogName: String, catalogRole: String) {
        val requiredPrivs =
            listOf(
                "TABLE_LIST",
                "TABLE_CREATE",
                "TABLE_DROP",
                "TABLE_READ_PROPERTIES",
                "TABLE_WRITE_PROPERTIES",
                "TABLE_WRITE_DATA",
                "NAMESPACE_LIST",
                "NAMESPACE_CREATE",
                "NAMESPACE_READ_PROPERTIES",
            )

        requiredPrivs.forEach { priv ->
            val body = """{"grant":{"type":"catalog","privilege":"$priv"}}"""
            val res =
                putJsonAdmin(
                    "/catalogs/$catalogName/catalog-roles/$catalogRole/grants",
                    body,
                )
            if (res.statusCode() !in listOf(200, 201, 204, 409)) {
                error(
                    "Grant privilege $priv to $catalogRole failed: ${res.statusCode()} ${res.body()}"
                )
            }
        }
    }

    /**
     * Creates a complete Polaris authentication and authorization setup:
     * 1. Creates a principal (service account) and retrieves OAuth credentials
     * 2. Creates principal role (realm-wide) and catalog role (catalog-specific)
     * 3. Links catalog role to principal role for the specific catalog
     * 4. Grants required privileges to the catalog role
     * 5. Attaches principal role to the principal
     *
     * This establishes the permission chain: Principal -> Principal Role -> Catalog Role ->
     * Privileges
     */
    private fun createPrincipalAndGrants() {
        val principalName = "$PRINCIPAL_BASENAME-${System.currentTimeMillis()}"

        // Step 1: Create principal and retrieve OAuth credentials (clientId and clientSecret)
        val createPrincipalRes = postJsonAdmin("/principals", """{"name":"$principalName"}""")
        if (createPrincipalRes.statusCode() !in 200..299) {
            error(
                "Principal create failed: ${createPrincipalRes.statusCode()} ${createPrincipalRes.body()}"
            )
        }
        val id =
            "\"clientId\"\\s*:\\s*\"([^\"]+)\""
                .toRegex()
                .find(createPrincipalRes.body())
                ?.groupValues
                ?.get(1)
        val secret =
            "\"clientSecret\"\\s*:\\s*\"([^\"]+)\""
                .toRegex()
                .find(createPrincipalRes.body())
                ?.groupValues
                ?.get(1)
        require(!id.isNullOrBlank() && !secret.isNullOrBlank()) {
            "Could not parse principal credentials from: ${createPrincipalRes.body()}"
        }
        appClientId = id
        appClientSecret = secret

        // Step 2: Create principal role (realm-wide) and catalog role (catalog-specific)
        postIgnore409("/principal-roles", """{"name":"$PRINCIPAL_ROLE"}""")
        postIgnore409("/catalogs/$CATALOG_NAME/catalog-roles", """{"name":"$CATALOG_ROLE"}""")

        // Step 3: Link catalog role to principal role for the specific catalog
        val grantBody = """{"catalogRole":{"name":"$CATALOG_ROLE"}}"""
        val grantRes =
            putJsonAdmin(
                "/principal-roles/$PRINCIPAL_ROLE/catalog-roles/$CATALOG_NAME",
                grantBody,
            )
        if (grantRes.statusCode() !in listOf(200, 201, 204, 409)) {
            error(
                "Grant catalog-role -> principal-role failed: ${grantRes.statusCode()} ${grantRes.body()}"
            )
        }

        // Step 4: Grant required privileges to the catalog role
        // Option A: Grant specific granular privileges (currently used)
        grantAirbytePrivileges(CATALOG_NAME, CATALOG_ROLE)
        // Option B: Grant broad CATALOG_MANAGE_CONTENT privilege (alternative, simpler approach)
        // grantCatalogManageContentPrivilege()

        // Step 5: Attach the principal role to the principal (completes the permission chain)
        attachPrincipalRoleToPrincipal(principalName)
    }

    /**
     * Alternative to grantAirbytePrivileges: Grants the broad CATALOG_MANAGE_CONTENT privilege.
     * This single privilege allows managing tables and namespaces in the catalog. Simpler than
     * granting individual privileges, but less granular.
     *
     * Currently unused in favor of specific granular privileges for better security.
     */
    @Suppress("unused")
    private fun grantCatalogManageContentPrivilege() {
        val privilegeBody = """{"grant":{"type":"catalog","privilege":"CATALOG_MANAGE_CONTENT"}}"""
        val privRes =
            putJsonAdmin(
                "/catalogs/$CATALOG_NAME/catalog-roles/$CATALOG_ROLE/grants",
                privilegeBody,
            )
        if (privRes.statusCode() !in listOf(200, 201, 204, 409)) {
            error(
                "Grant privilege to catalog-role failed: ${privRes.statusCode()} ${privRes.body()}"
            )
        }
    }

    /**
     * Attaches the principal role to the principal, completing the authorization setup. This allows
     * the principal to inherit all permissions from the principal role.
     */
    private fun attachPrincipalRoleToPrincipal(principalName: String) {
        val body = """{"principalRole":{"name":"$PRINCIPAL_ROLE"}}"""
        val res =
            putJsonAdmin(
                "/principals/$principalName/principal-roles",
                body,
            )
        if (res.statusCode() !in listOf(200, 201, 204, 409)) {
            error("Attach principal-role -> principal failed: ${res.statusCode()} ${res.body()}")
        }
    }
}
