/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.lowcode

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory
import dev.failsafe.RetryPolicy
import io.airbyte.cdk.load.check.dlq.DlqChecker
import io.airbyte.cdk.load.checker.CompositeDlqChecker
import io.airbyte.cdk.load.checker.HttpRequestChecker
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.command.Overwrite
import io.airbyte.cdk.load.command.SoftDelete
import io.airbyte.cdk.load.command.Update
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfigProvider
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
import io.airbyte.cdk.load.model.discovery.CompositeOperations as CompositeOperationsModel
import io.airbyte.cdk.load.model.discovery.Operation as OperationModel
import io.airbyte.cdk.load.model.discovery.StaticOperation
import io.airbyte.cdk.load.model.http.HttpMethod
import io.airbyte.cdk.load.model.http.HttpRequester as HttpRequesterModel
import io.airbyte.cdk.load.model.http.authenticator.Authenticator as AuthenticatorModel
import io.airbyte.cdk.load.model.http.authenticator.BasicAccessAuthenticator as BasicAccessAuthenticatorModel
import io.airbyte.cdk.load.model.http.authenticator.OAuthAuthenticator as OAuthAuthenticatorModel
import io.airbyte.cdk.load.model.sync_mode.Append as AppendModel
import io.airbyte.cdk.load.model.sync_mode.Dedupe as DedupeModel
import io.airbyte.cdk.load.model.sync_mode.Overwrite as OverwriteModel
import io.airbyte.cdk.load.model.sync_mode.SoftDelete as SoftDeleteModel
import io.airbyte.cdk.load.model.sync_mode.SyncMode as SyncModeModel
import io.airbyte.cdk.load.model.sync_mode.Update as UpdateModel
import io.airbyte.cdk.util.ResourceUtils
import okhttp3.Interceptor
import okhttp3.OkHttpClient

class DeclarativeDestinationFactory<T>(private val config: T) where
T : DestinationConfiguration,
T : ObjectStorageConfigProvider {
    private val stringInterpolator: StringInterpolator = StringInterpolator()

    fun createDestinationChecker(dlqChecker: DlqChecker): CompositeDlqChecker<T> {
        val mapper = ObjectMapper(YAMLFactory())
        val manifestContent = ResourceUtils.readResource("manifest.yaml")
        val manifest: DeclarativeDestinationModel =
            mapper.readValue(manifestContent, DeclarativeDestinationModel::class.java)
        return CompositeDlqChecker(createChecker(manifest.checker), dlqChecker)
    }

    fun createCompositeOperationsProvider(): CompositeOperationProvider {
        val mapper = ObjectMapper(YAMLFactory())
        val manifestContent = ResourceUtils.readResource("manifest.yaml")
        val manifest: DeclarativeDestinationModel =
            mapper.readValue(manifestContent, DeclarativeDestinationModel::class.java)
        return createCompositeOperationsProvider(manifest.discovery)
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
    ): HttpRequestChecker<T> =
        when (model) {
            is HttpRequestCheckerModel -> HttpRequestChecker(model.requester.toRequester())
        }

    private fun createCompositeOperationsProvider(
        model: CompositeOperationsModel
    ): CompositeOperationProvider =
        CompositeOperationProvider(model.operations.map { createOperationsProvider(it) })

    private fun createOperationsProvider(model: OperationModel): OperationProvider =
        when (model) {
            is StaticOperation ->
                StaticOperationProvider(
                    model.objectName,
                    mapSyncMode(model.syncMode),
                    JsonSchemaToAirbyteType(
                            unionBehavior = JsonSchemaToAirbyteType.UnionBehavior.DEFAULT
                        )
                        .convert(model.schema),
                    model.matchingKeys ?: emptyList()
                )
        }

    private fun mapSyncMode(
        model: SyncModeModel,
    ): ImportType =
        when (model) {
            is AppendModel -> Append
            is DedupeModel -> Dedupe(model.primaryKey, model.cursor)
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

    private fun createInterpolationContext(): Map<String, T> = mapOf("config" to config)
}
