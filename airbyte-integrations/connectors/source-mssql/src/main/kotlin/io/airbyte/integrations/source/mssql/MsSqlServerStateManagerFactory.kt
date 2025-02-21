package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.MetaFieldDecorator
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.output.CatalogValidationFailureHandler
import io.airbyte.cdk.output.FieldTypeMismatch
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.read.StateManagerFactory
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton


/**
 * This is only needed to maintain compatibility with old catalogs where the catalog schema
 * might not match the actual DB schema.
 * Pre-bulk CDK, such a difference was ignored, but the default behavior of the new CDK
 * is to be more strict. As we don't want to break a lot of customers during such a risky
 * connector upgrade, we're ignoring catalog changes for now
 */
@Singleton
@Primary
class MsSqlServerStateManagerFactory(
    metadataQuerierFactory: MetadataQuerier.Factory<SourceConfiguration>,
    metaFieldDecorator: MetaFieldDecorator,
    outputConsumer: OutputConsumer,
    handler: CatalogValidationFailureHandler,
    ): StateManagerFactory(metadataQuerierFactory, metaFieldDecorator, outputConsumer, handler) {

    override fun checkColumnTypes(
        streamId: StreamIdentifier,
        fieldName: String,
        expectedAirbyteSchemaType: AirbyteSchemaType,
        actualColumn: Field
    ): Field? {
        super.checkColumnTypes(streamId, fieldName, expectedAirbyteSchemaType, actualColumn)
        return actualColumn
    }
}
