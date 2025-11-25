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
import io.airbyte.cdk.load.command.SoftDelete
import io.airbyte.cdk.load.command.Update
import io.airbyte.cdk.load.command.dlq.DisabledObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.ObjectStorageSpec
import io.airbyte.cdk.load.command.dlq.toObjectStorageConfig
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.data.json.JsonSchemaToAirbyteType
import io.airbyte.cdk.load.discoverer.destinationobject.DestinationObjectProvider
import io.airbyte.cdk.load.discoverer.destinationobject.DynamicDestinationObjectProvider
import io.airbyte.cdk.load.discoverer.destinationobject.StaticDestinationObjectProvider
import io.airbyte.cdk.load.discoverer.operation.CompositeOperationProvider
import io.airbyte.cdk.load.discoverer.operation.DestinationOperationAssembler
import io.airbyte.cdk.load.discoverer.operation.DynamicOperationProvider
import io.airbyte.cdk.load.discoverer.operation.InsertionMethod
import io.airbyte.cdk.load.discoverer.operation.JsonNodePredicate
import io.airbyte.cdk.load.discoverer.operation.OperationProvider
import io.airbyte.cdk.load.discoverer.operation.StaticOperationProvider
import io.airbyte.cdk.load.http.HttpRequester
import io.airbyte.cdk.load.http.RequestMethod
import io.airbyte.cdk.load.http.Retriever
import io.airbyte.cdk.load.http.authentication.BasicAccessAuthenticator
import io.airbyte.cdk.load.http.authentication.OAuthAuthenticator
import io.airbyte.cdk.load.http.okhttp.AirbyteOkHttpClient
import io.airbyte.cdk.load.interpolation.StringInterpolator
import io.airbyte.cdk.load.model.DeclarativeDestination as DeclarativeDestinationModel
import io.airbyte.cdk.load.model.checker.Checker as CheckerModel
import io.airbyte.cdk.load.model.checker.HttpRequestChecker as HttpRequestCheckerModel
import io.airbyte.cdk.load.model.destination_import_mode.DestinationImportMode as DestinationImportModeModel
import io.airbyte.cdk.load.model.destination_import_mode.Insert as InsertModel
import io.airbyte.cdk.load.model.destination_import_mode.SoftDelete as SoftDeleteModel
import io.airbyte.cdk.load.model.destination_import_mode.Update as UpdateModel
import io.airbyte.cdk.load.model.destination_import_mode.Upsert as UpsertModel
import io.airbyte.cdk.load.model.discover.AirbyteType as AirbyteTypeModel
import io.airbyte.cdk.load.model.discover.ArrayType as ArrayTypeModel
import io.airbyte.cdk.load.model.discover.ArrayTypeWithoutSchema as ArrayTypeWithoutSchemaModel
import io.airbyte.cdk.load.model.discover.BooleanType as BooleanTypeModel
import io.airbyte.cdk.load.model.discover.CatalogOperation as CatalogOperationModel
import io.airbyte.cdk.load.model.discover.CompositeCatalogOperations as CompositeCatalogOperationsModel
import io.airbyte.cdk.load.model.discover.DateType as DateTypeModel
import io.airbyte.cdk.load.model.discover.DestinationObjects as DestinationObjectsModel
import io.airbyte.cdk.load.model.discover.DynamicCatalogOperation as DynamicCatalogOperationModel
import io.airbyte.cdk.load.model.discover.DynamicDestinationObjects as DynamicDestinationObjectsModel
import io.airbyte.cdk.load.model.discover.InsertionMethod as InsertionMethodModel
import io.airbyte.cdk.load.model.discover.IntegerType as IntegerTypeModel
import io.airbyte.cdk.load.model.discover.NumberType as NumberTypeModel
import io.airbyte.cdk.load.model.discover.ObjectType as ObjectTypeModel
import io.airbyte.cdk.load.model.discover.ObjectTypeWithEmptySchema as ObjectTypeWithEmptySchemaModel
import io.airbyte.cdk.load.model.discover.ObjectTypeWithoutSchema as ObjectTypeWithoutSchemaModel
import io.airbyte.cdk.load.model.discover.SchemaConfiguration as SchemaConfigurationModel
import io.airbyte.cdk.load.model.discover.StaticCatalogOperation as StaticCatalogOperationModel
import io.airbyte.cdk.load.model.discover.StaticDestinationObjects as StaticDestinationObjectsModel
import io.airbyte.cdk.load.model.discover.StringType as StringTypeModel
import io.airbyte.cdk.load.model.discover.TimeTypeWithTimezone as TimeTypeWithTimezoneModel
import io.airbyte.cdk.load.model.discover.TimeTypeWithoutTimezone as TimeTypeWithoutTimezoneModel
import io.airbyte.cdk.load.model.discover.TimestampTypeWithTimezone as TimestampTypeWithTimezoneModel
import io.airbyte.cdk.load.model.discover.TimestampTypeWithoutTimezone as TimestampTypeWithoutTimezoneModel
import io.airbyte.cdk.load.model.discover.TypesMap as TypesMapModel
import io.airbyte.cdk.load.model.discover.UnionType as UnionTypeModel
import io.airbyte.cdk.load.model.discover.UnknownType as UnknownTypeModel
import io.airbyte.cdk.load.model.http.HttpMethod
import io.airbyte.cdk.load.model.http.HttpRequester as HttpRequesterModel
import io.airbyte.cdk.load.model.http.authenticator.Authenticator as AuthenticatorModel
import io.airbyte.cdk.load.model.http.authenticator.BasicAccessAuthenticator as BasicAccessAuthenticatorModel
import io.airbyte.cdk.load.model.http.authenticator.OAuthAuthenticator as OAuthAuthenticatorModel
import io.airbyte.cdk.load.model.retriever.Retriever as RetrieverModel
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
            is DynamicCatalogOperationModel -> model.toProvider()
        }

    private fun mapImportMode(
        model: DestinationImportModeModel,
    ): ImportType =
        when (model) {
            is InsertModel -> Append
            is UpsertModel -> Dedupe(emptyList(), emptyList())
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

    fun DynamicCatalogOperationModel.toProvider(): DynamicOperationProvider {
        val dynamicOperation = this
        return DynamicOperationProvider(
            createDestinationObjectProvider(dynamicOperation.objects),
            createDestinationOperationAssembler(dynamicOperation)
        )
    }

    private fun createDestinationObjectProvider(
        model: DestinationObjectsModel
    ): DestinationObjectProvider =
        when (model) {
            is StaticDestinationObjectsModel -> StaticDestinationObjectProvider(model.objects)
            is DynamicDestinationObjectsModel ->
                DynamicDestinationObjectProvider(
                    model.retriever.toRetriever(),
                    model.namePath ?: emptyList()
                )
        }

    private fun createDestinationOperationAssembler(
        model: DynamicCatalogOperationModel
    ): DestinationOperationAssembler {
        val propertiesPath: List<String> = model.schema.propertiesPath
        val insertionMethods: List<InsertionMethod> =
            model.insertionMethods.map { createInsertionMethod(model.schema, it) }
        val schemaRequester: HttpRequester? = model.schemaRetriever?.httpRequester?.toRequester()
        return DestinationOperationAssembler(propertiesPath, insertionMethods, schemaRequester)
    }

    fun RetrieverModel.toRetriever(): Retriever {
        val retriever = this
        val requester: HttpRequester = retriever.httpRequester.toRequester()
        return Retriever(requester, retriever.selector)
    }

    private fun createInsertionMethod(
        schemaModel: SchemaConfigurationModel,
        model: InsertionMethodModel
    ): InsertionMethod =
        InsertionMethod(
            mapImportMode(model.destinationImportMode),
            schemaModel.propertyNamePath,
            schemaModel.typePath,
            JsonNodePredicate(model.availabilityPredicate),
            model.matchingKeyPredicate?.let { JsonNodePredicate(model.matchingKeyPredicate) },
            JsonNodePredicate(model.requiredPredicate),
            schemaModel.typeMapping?.let { createTypeMapping(it) } ?: emptyMap(),
        )

    private fun createTypeMapping(model: List<TypesMapModel>): Map<String, AirbyteType> {
        /*
         *  mapping.airbyteType[0] is not what we want long term. The protocol allows for an API
         *  type to map to multiple types, but this doesn't map to the runtime InsertionMethod's
         *  typeMapping which is 1:1 between API type -> Airbyte type. If multiple are provided
         *  we fail loudly for now, but in a subsequent change, the InsertionMethod.typeMapper
         *  should become Map<String, List<AirbyteType> to support this. But out of scope for
         *  the initial change to support dynamic schema discovery.
         */
        model.forEach { mapping ->
            if (mapping.airbyteType.size != 1) {
                throw IllegalArgumentException(
                    "Mapping with api_type(s) ${mapping.apiType} maps to ${mapping.airbyteType.size}, but only 1 airbyte_type is allowed."
                )
            }
        }

        return model
            .flatMap { mapping ->
                mapping.apiType.map { apiType -> apiType to mapping.airbyteType[0].toAirbyteType() }
            }
            .toMap()
    }

    fun AirbyteTypeModel.toAirbyteType(): AirbyteType =
        when (this) {
            is StringTypeModel -> StringType
            is BooleanTypeModel -> BooleanType
            is IntegerTypeModel -> IntegerType
            is NumberTypeModel -> NumberType
            is DateTypeModel -> DateType
            is TimestampTypeWithTimezoneModel -> TimestampTypeWithTimezone
            is TimestampTypeWithoutTimezoneModel -> TimestampTypeWithoutTimezone
            is TimeTypeWithTimezoneModel -> TimeTypeWithTimezone
            is TimeTypeWithoutTimezoneModel -> TimeTypeWithoutTimezone
            is ArrayTypeModel ->
                ArrayType(FieldType(this.items.type.toAirbyteType(), this.items.nullable))
            is ArrayTypeWithoutSchemaModel -> ArrayTypeWithoutSchema
            is ObjectTypeModel ->
                ObjectType(
                    this.properties
                        .map { (key, property) ->
                            key to FieldType(property.type.toAirbyteType(), property.nullable)
                        }
                        .toMap() as LinkedHashMap,
                    this.additionalProperties,
                    this.required ?: emptyList()
                )
            is ObjectTypeWithEmptySchemaModel -> ObjectTypeWithEmptySchema
            is ObjectTypeWithoutSchemaModel -> ObjectTypeWithoutSchema
            is UnionTypeModel ->
                UnionType(
                    this.options.map { option -> option.toAirbyteType() }.toSet(),
                    this.isLegacyUnion
                )
            is UnknownTypeModel -> UnknownType(this.schema)
        }
}
