/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.lowcode

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory
import dev.failsafe.RetryPolicy
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.check.dlq.DlqChecker
import io.airbyte.cdk.load.checker.CompositeDlqChecker
import io.airbyte.cdk.load.checker.HttpRequestChecker
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.command.Overwrite
import io.airbyte.cdk.load.command.SoftDelete
import io.airbyte.cdk.load.command.Update
import io.airbyte.cdk.load.command.dlq.DisabledObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.ObjectStorageSpec
import io.airbyte.cdk.load.command.dlq.toObjectStorageConfig
import io.airbyte.cdk.load.data.json.JsonSchemaToAirbyteType
import io.airbyte.cdk.load.discoverer.operation.CompositeOperationProvider
import io.airbyte.cdk.load.discoverer.operation.OperationProvider
import io.airbyte.cdk.load.discoverer.operation.StaticOperationProvider
import io.airbyte.cdk.load.http.HttpRequester
import io.airbyte.cdk.load.http.RequestMethod
import io.airbyte.cdk.load.http.authentication.BasicAccessAuthenticator
import io.airbyte.cdk.load.http.authentication.OAuthAuthenticator
import io.airbyte.cdk.load.http.okhttp.AirbyteOkHttpClient
import io.airbyte.cdk.load.interpolation.StringInterpolator
import io.airbyte.cdk.load.model.DeclarativeDestination as DeclarativeDestinationModel
import io.airbyte.cdk.load.model.checker.Checker as CheckerModel
import io.airbyte.cdk.load.model.checker.HttpRequestChecker as HttpRequestCheckerModel
import io.airbyte.cdk.load.model.destination_import_mode.Append as AppendModel
import io.airbyte.cdk.load.model.destination_import_mode.Dedupe as DedupeModel
import io.airbyte.cdk.load.model.destination_import_mode.DestinationImportMode as DestinationImportModeModel
import io.airbyte.cdk.load.model.destination_import_mode.Overwrite as OverwriteModel
import io.airbyte.cdk.load.model.destination_import_mode.SoftDelete as SoftDeleteModel
import io.airbyte.cdk.load.model.destination_import_mode.Update as UpdateModel
import io.airbyte.cdk.load.model.discover.CatalogOperation as CatalogOperationModel
import io.airbyte.cdk.load.model.discover.CompositeCatalogOperations as CompositeCatalogOperationsModel
import io.airbyte.cdk.load.model.discover.StaticCatalogOperation as StaticCatalogOperationModel
import io.airbyte.cdk.load.model.http.HttpMethod
import io.airbyte.cdk.load.model.http.HttpRequester as HttpRequesterModel
import io.airbyte.cdk.load.model.http.authenticator.Authenticator as AuthenticatorModel
import io.airbyte.cdk.load.model.http.authenticator.BasicAccessAuthenticator as BasicAccessAuthenticatorModel
import io.airbyte.cdk.load.model.http.authenticator.OAuthAuthenticator as OAuthAuthenticatorModel
import io.airbyte.cdk.load.spec.DeclarativeCdkConfiguration
import io.airbyte.cdk.load.spec.DeclarativeSpecificationFactory
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import okhttp3.Interceptor
import okhttp3.OkHttpClient

class DeclarativeDestinationFactory(config: JsonNode?) {
    private val stringInterpolator: StringInterpolator = StringInterpolator()
    private val manifest: DeclarativeDestinationModel = createManifest()
    // TODO at some point, we might want to validate the config against the spec to improve error
    // messages
    val config: JsonNode? = config
    val cdkConfiguration = createCdkConfiguration()

    companion object {
        fun createManifest(): DeclarativeDestinationModel {
            val mapper = ObjectMapper(YAMLFactory())
            val manifestContent = ResourceUtils.readResource("manifest.yaml")
            val manifest: DeclarativeDestinationModel =
                mapper.readValue(manifestContent, DeclarativeDestinationModel::class.java)
            return manifest
        }
    }

    fun createCdkConfiguration(): DeclarativeCdkConfiguration {
        if (config == null || config.get("object_storage_config") == null) {
            return DeclarativeCdkConfiguration(DisabledObjectStorageConfig())
        }

        val objectStorageConfig =
            ValidatedJsonUtils.parseUnvalidated(
                    config.get("object_storage_config"),
                    ObjectStorageSpec::class.java
                )
                .toObjectStorageConfig()
        return DeclarativeCdkConfiguration(objectStorageConfig)
    }

    fun createSpecificationFactory(): DeclarativeSpecificationFactory {
        return DeclarativeSpecificationFactory(manifest.spec)
    }

    fun createDestinationChecker(dlqChecker: DlqChecker): CompositeDlqChecker {
        return CompositeDlqChecker(
            createChecker(manifest.checker),
            dlqChecker,
            cdkConfiguration.objectStorageConfig
        )
    }

    fun createOperationProvider(): OperationProvider {
        // todo: 'discovery' component in the long term should be a required field, but since
        //  the first PR only implements static discovery not dynamic, we don't want to make the
        //  component required until connectors like Hubspot can define it.
        if (manifest.discover == null) {
            throw IllegalArgumentException(
                "manifest.yaml is missing expected 'discovery' component"
            )
        } else {
            return createOperationProvider(manifest.discover)
        }
    }

    private fun createAuthenticator(
        model: AuthenticatorModel,
    ): Interceptor =
        when (model) {
            is BasicAccessAuthenticatorModel -> model.toInterceptor(createInterpolationContext())
            is OAuthAuthenticatorModel -> model.toInterceptor(createInterpolationContext())
        }

    private fun createChecker(
        model: CheckerModel,
    ): HttpRequestChecker =
        when (model) {
            is HttpRequestCheckerModel -> HttpRequestChecker(model.requester.toRequester())
        }

    private fun createOperationProvider(model: CatalogOperationModel): OperationProvider =
        when (model) {
            is CompositeCatalogOperationsModel ->
                CompositeOperationProvider(model.operations.map { createOperationProvider(it) })
            is StaticCatalogOperationModel ->
                StaticOperationProvider(
                    model.objectName,
                    mapImportMode(model.destinationImportMode),
                    JsonSchemaToAirbyteType(
                            unionBehavior = JsonSchemaToAirbyteType.UnionBehavior.DEFAULT
                        )
                        .convert(model.schema),
                    model.matchingKeys ?: emptyList()
                )
        }

    private fun mapImportMode(
        model: DestinationImportModeModel,
    ): ImportType =
        when (model) {
            is AppendModel -> Append
            is DedupeModel -> Dedupe(model.primaryKey ?: emptyList(), model.cursor ?: emptyList())
            is OverwriteModel -> Overwrite
            is UpdateModel -> Update
            is SoftDeleteModel -> SoftDelete
        }

    fun BasicAccessAuthenticatorModel.toInterceptor(
        interpolationContext: Map<String, Any>
    ): BasicAccessAuthenticator =
        BasicAccessAuthenticator(
            stringInterpolator.interpolate(this.username, interpolationContext),
            stringInterpolator.interpolate(this.password, interpolationContext),
        )

    fun OAuthAuthenticatorModel.toInterceptor(
        interpolationContext: Map<String, Any>
    ): OAuthAuthenticator =
        OAuthAuthenticator(
            stringInterpolator.interpolate(this.url, interpolationContext),
            stringInterpolator.interpolate(this.clientId, interpolationContext),
            stringInterpolator.interpolate(this.clientSecret, interpolationContext),
            stringInterpolator.interpolate(this.refreshToken, interpolationContext),
        )

    fun HttpRequesterModel.toRequester(): HttpRequester {
        val requester = this
        val okhttpClient: OkHttpClient =
            OkHttpClient.Builder()
                .apply {
                    if (requester.authenticator != null) {
                        this.addInterceptor(createAuthenticator(requester.authenticator))
                    }
                }
                .build()
        return HttpRequester(
            AirbyteOkHttpClient(okhttpClient, RetryPolicy.ofDefaults()),
            this.method.toRequestMethod(),
            this.url,
        )
    }

    fun HttpMethod.toRequestMethod(): RequestMethod =
        when (this) {
            HttpMethod.GET -> RequestMethod.GET
            HttpMethod.POST -> RequestMethod.POST
            HttpMethod.PUT -> RequestMethod.PUT
            HttpMethod.PATCH -> RequestMethod.PATCH
            HttpMethod.DELETE -> RequestMethod.DELETE
            HttpMethod.HEAD -> RequestMethod.HEAD
            HttpMethod.OPTIONS -> RequestMethod.OPTIONS
        }

    private fun createInterpolationContext(): Map<String, Any> =
        mapOf("config" to Jsons.convertValue(config, MutableMap::class.java))
}
