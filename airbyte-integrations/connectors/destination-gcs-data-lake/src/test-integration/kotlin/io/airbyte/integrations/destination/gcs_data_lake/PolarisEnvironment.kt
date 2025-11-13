/*
 * Copyright (c) 2025 Airbyte, Inc.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import java.io.File
import java.net.URI
import java.net.URLEncoder
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.time.Duration
import java.util.Base64
import java.util.concurrent.atomic.AtomicBoolean

/**
 * WARNING: Tightly coupled with docker-compose.yml. See:
 * src/test-integration/resources/polaris/docker-compose.gcs.yml
 */
object PolarisEnvironment {

    // Compose file for the GCS variant
    private val composeFile = File("src/test-integration/resources/polaris/docker-compose.yml")
    private val startedOnce = AtomicBoolean(false)

    private const val POLARIS_REST_BASE = "http://localhost:8181/api"
    private const val POLARIS_MGMT_BASE = "http://localhost:8181/api/management/v1"
    private const val OAUTH_TOKEN_URL = "http://localhost:8181/api/catalog/v1/oauth/tokens"

    private const val POLARIS_HEALTH_PRIMARY = "http://localhost:8182/q/health/ready"
    private const val POLARIS_HEALTH_FALLBACK = "http://localhost:8182/health/ready"

    private const val REALM_HEADER_NAME = "Polaris-Realm"
    private const val REALM = "POLARIS"
    private const val BOOTSTRAP_ID = "root"
    private const val BOOTSTRAP_SECRET = "s3cr3t"

    // Catalog & principals/roles
    private const val CATALOG_NAME = "quickstart_catalog"
    private const val PRINCIPAL_BASENAME = "quickstart_user"
    private const val PRINCIPAL_ROLE = "quickstart_user_role"
    private const val CATALOG_ROLE = "quickstart_catalog_role"

    // ---- GCS specifics ----
    // Ensure this bucket exists beforehand
    private const val BUCKET = "YOUR_BUCKET_NAME"

    // Service-account email with access to the bucket (NOT key contents).
    // Must include the "serviceAccount:" prefix (Polaris expects this form).
    private const val GCS_SERVICE_ACCOUNT_EMAIL = "serviceAccount:YOUR_SERVICE_ACCOUNT_EMAIL"

    // GCP location for the bucket
    private const val GCS_BUCKET_LOCATION = "YOUR_GCS_BUCKET_LOCATION"

    // Path to service account credentials file
    private val GCS_SA_FILE = File("src/test-integration/resources/polaris/gcs-creds/gcs-sa.json")

    // Lazy-loaded service account credentials from file
    private val GCS_SERVICE_ACCOUNT_CREDS: String by lazy {
        if (!GCS_SA_FILE.exists()) {
            error(
                "Service account file not found: ${GCS_SA_FILE.absolutePath}. Please update the file with your GCS credentials."
            )
        }
        val content = GCS_SA_FILE.readText().trim()
        if (content.contains("TODO")) {
            error(
                "Please update ${GCS_SA_FILE.absolutePath} with your actual GCS service account credentials"
            )
        }
        // Escape the JSON for embedding in a JSON string
        content.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "")
    }

    @Volatile private var appClientId: String? = null
    @Volatile private var appClientSecret: String? = null

    @Volatile private var bearerToken: String? = null

    private val http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).build()

    /** Idempotently boot Polaris + Postgres, wait for health, then create catalog + auth. */
    fun startServices() {
        if (startedOnce.compareAndSet(false, true)) {
            val up =
                ProcessBuilder("docker", "compose", "-f", composeFile.absolutePath, "up", "-d")
                    .inheritIO()
                    .start()
            val exitCode = up.waitFor()
            if (exitCode != 0) error("Failed to start compose services. Exit code: $exitCode")

            if (
                !waitForOrFalse(POLARIS_HEALTH_PRIMARY, 150) &&
                    !waitForOrFalse(POLARIS_HEALTH_FALLBACK, 60)
            ) {
                error("Polaris not healthy at $POLARIS_HEALTH_PRIMARY nor $POLARIS_HEALTH_FALLBACK")
            }

            requireApiReady()
            createCatalogIfNeeded()
            createPrincipalAndGrants()
        }
    }

    /** Tear down stack + clear cached creds. */
    fun stopServices() {
        if (startedOnce.compareAndSet(true, false)) {
            ProcessBuilder("docker", "compose", "-f", composeFile.absolutePath, "down", "-v")
                .inheritIO()
                .start()
                .waitFor()
            bearerToken = null
            appClientId = null
            appClientSecret = null
        }
    }

    /**
     * Returns JSON config for GCS Data Lake tests:
     * - REST (Polaris) catalog with client_id/client_secret
     * - Warehouse at gs://BUCKET/
     */
    fun getConfig(): String {
        startServices()
        val serverUri = "$POLARIS_REST_BASE/catalog"

        val a =
            """
        {
          "catalog_type": {
            "catalog_type": "POLARIS",
            "server_uri": "$serverUri",
            "catalog_name": "$CATALOG_NAME",
            "client_id": "$appClientId",
            "client_secret": "$appClientSecret"
          },
          "namespace": "<DEFAULT_NAMESPACE_PLACEHOLDER>",
          "gcs_bucket_name" : "$BUCKET",
          "service_account_json" : "$GCS_SERVICE_ACCOUNT_CREDS",
          "warehouse_location": "gs://$BUCKET/",
          "gcp_location" : "$GCS_BUCKET_LOCATION",
          "main_branch_name": "main"
        }
        """.trimIndent()

        return a
    }

    private fun waitFor(url: String, timeoutSec: Int) {
        val deadline = System.nanoTime() + Duration.ofSeconds(timeoutSec.toLong()).toNanos()
        var lastErr: Throwable? = null
        while (System.nanoTime() < deadline) {
            try {
                val res =
                    http.send(
                        HttpRequest.newBuilder(URI.create(url))
                            .timeout(Duration.ofSeconds(3))
                            .GET()
                            .build(),
                        HttpResponse.BodyHandlers.discarding()
                    )
                if (res.statusCode() in 200..299) return
                lastErr = RuntimeException("HTTP ${res.statusCode()}")
            } catch (t: Throwable) {
                lastErr = t
            }
            Thread.sleep(500)
        }
        throw IllegalStateException("Timeout waiting for $url", lastErr)
    }

    private fun waitForOrFalse(url: String, timeoutSec: Int): Boolean =
        try {
            waitFor(url, timeoutSec)
            true
        } catch (_: Throwable) {
            false
        }

    private fun adminBasicAuthHeader(): String {
        val token = "$BOOTSTRAP_ID:$BOOTSTRAP_SECRET"
        val b64 = Base64.getEncoder().encodeToString(token.toByteArray())
        return "Basic $b64"
    }

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
        if (res.statusCode() !in 200..299)
            error("Token request failed: ${res.statusCode()} ${res.body()}")
        val token =
            "\"access_token\"\\s*:\\s*\"([^\"]+)\"".toRegex().find(res.body())?.groupValues?.get(1)
        require(!token.isNullOrBlank()) { "No access_token in response: ${res.body()}" }
        return token!!
    }

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

    private fun requireApiReady() {
        val res = sendWithAutoRefresh { token ->
            HttpRequest.newBuilder(URI.create("$POLARIS_MGMT_BASE/catalogs"))
                .timeout(Duration.ofSeconds(10))
                .header(REALM_HEADER_NAME, REALM)
                .header("Authorization", "Bearer $token")
                .GET()
                .build()
        }
        if (res.statusCode() !in 200..299)
            error("Polaris Management API not ready: ${res.statusCode()} ${res.body()}")
    }

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

    /** Create (or ensure) a GCS-backed INTERNAL catalog. */
    private fun createCatalogIfNeeded() {
        val body =
            """
          {
            "catalog": {
              "type": "INTERNAL",
              "name": "$CATALOG_NAME",
              "properties": {
                "default-base-location": "gs://$BUCKET/"
              },
              "storageConfigInfo": {
                "storageType": "GCS",
                "serviceAccount": "$GCS_SERVICE_ACCOUNT_EMAIL"
              }
            }
          }
        """.trimIndent()

        val res = postJsonAdmin("/catalogs", body)
        when (res.statusCode()) {
            in 200..299 -> Unit
            409 -> Unit
            else -> error("Catalog create failed: ${res.statusCode()} ${res.body()}")
        }
    }

    private fun grantAirbytePrivileges(catalogName: String, catalogRole: String) {
        val required =
            listOf(
                "TABLE_LIST",
                "TABLE_CREATE",
                "TABLE_DROP",
                "TABLE_READ_PROPERTIES",
                "TABLE_WRITE_PROPERTIES",
                "TABLE_WRITE_DATA",
                "NAMESPACE_LIST",
                "NAMESPACE_CREATE",
                "NAMESPACE_READ_PROPERTIES"
            )
        required.forEach { priv ->
            val body = """{"grant":{"type":"catalog","privilege":"$priv"}}"""
            val res = putJsonAdmin("/catalogs/$catalogName/catalog-roles/$catalogRole/grants", body)
            if (res.statusCode() !in listOf(200, 201, 204, 409)) {
                error("Grant $priv -> $catalogRole failed: ${res.statusCode()} ${res.body()}")
            }
        }
    }

    private fun createPrincipalAndGrants() {
        val principalName = "$PRINCIPAL_BASENAME-${System.currentTimeMillis()}"

        // 1) Principal -> clientId/clientSecret for REST catalog auth
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
            "Could not parse principal credentials: ${createPrincipalRes.body()}"
        }
        appClientId = id
        appClientSecret = secret

        // 2) Roles
        postIgnore409("/principal-roles", """{"name":"$PRINCIPAL_ROLE"}""")
        postIgnore409("/catalogs/$CATALOG_NAME/catalog-roles", """{"name":"$CATALOG_ROLE"}""")

        // 3) Link catalog-role -> principal-role for this catalog
        val linkBody = """{"catalogRole":{"name":"$CATALOG_ROLE"}}"""
        val linkRes =
            putJsonAdmin("/principal-roles/$PRINCIPAL_ROLE/catalog-roles/$CATALOG_NAME", linkBody)
        if (linkRes.statusCode() !in listOf(200, 201, 204, 409)) {
            error(
                "Link catalog-role -> principal-role failed: ${linkRes.statusCode()} ${linkRes.body()}"
            )
        }

        // 4) Privileges
        grantAirbytePrivileges(CATALOG_NAME, CATALOG_ROLE)

        // 5) Attach role to principal
        val attachBody = """{"principalRole":{"name":"$PRINCIPAL_ROLE"}}"""
        val attachRes = putJsonAdmin("/principals/$principalName/principal-roles", attachBody)
        if (attachRes.statusCode() !in listOf(200, 201, 204, 409)) {
            error(
                "Attach principal-role -> principal failed: ${attachRes.statusCode()} ${attachRes.body()}"
            )
        }
    }
}
