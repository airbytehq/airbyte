package io.airbyte.cdk.load.lowcode

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory
import dev.failsafe.RetryPolicy
import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.checker.HttpRequestChecker
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.http.HttpRequester
import io.airbyte.cdk.load.http.RequestMethod
import io.airbyte.cdk.load.http.authentication.BasicAccessAuthenticator
import io.airbyte.cdk.load.http.okhttp.AirbyteOkHttpClient
import io.airbyte.cdk.load.interpolation.StringInterpolator
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.integrations.source.postgres.internal.models.BasicAccessAuthenticator as BasicAccessAuthenticatorModel
import io.airbyte.integrations.source.postgres.internal.models.DeclarativeComponentsSchema
import io.airbyte.integrations.source.postgres.internal.models.HttpRequester as HttpRequesterModel
import okhttp3.OkHttpClient

class Factory<T: DestinationConfiguration> (
    private val config: T
) {
    private val interpolator: StringInterpolator = StringInterpolator()

    fun createDestinationChecker() : DestinationChecker<T> {
        val mapper = ObjectMapper(YAMLFactory())
        val manifestContent = ResourceUtils.readResource("manifest_example.yaml")
        val manifest: DeclarativeComponentsSchema = mapper.readValue(manifestContent, DeclarativeComponentsSchema::class.java)
        return HttpRequestChecker<T>(createHttpRequester(manifest.checker.requester))
    }

    private fun createHttpRequester(model: HttpRequesterModel): HttpRequester {
        val okhttpClient: OkHttpClient =
            OkHttpClient.Builder().addInterceptor(createBasicAccessAuthenticator(model.authenticator)).build()
        return HttpRequester(
            AirbyteOkHttpClient(okhttpClient, RetryPolicy.ofDefaults()),
            assembleRequestMethod(model.method),
            model.url,
        )
    }

    private fun createBasicAccessAuthenticator(model: BasicAccessAuthenticatorModel): BasicAccessAuthenticator {
        val interpolationContext = createInterpolationContext()
        return BasicAccessAuthenticator(
            interpolator.interpolate(model.username, interpolationContext),
            interpolator.interpolate(model.password, interpolationContext),
        )
    }

    private fun createInterpolationContext(): Map<String, T> = mapOf("config" to config)

    private fun assembleRequestMethod(method: HttpRequesterModel.Method): RequestMethod {
        return when (method) {
            HttpRequesterModel.Method.GET -> RequestMethod.GET
            HttpRequesterModel.Method.POST -> RequestMethod.POST
            HttpRequesterModel.Method.PUT -> RequestMethod.PUT
            HttpRequesterModel.Method.PATCH -> RequestMethod.PATCH
            HttpRequesterModel.Method.DELETE -> RequestMethod.DELETE
            HttpRequesterModel.Method.HEAD -> RequestMethod.HEAD
            HttpRequesterModel.Method.OPTIONS -> RequestMethod.OPTIONS
        }
    }

}
