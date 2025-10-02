package io.airbyte.integrations.destination.motherduck.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.write.db.DbConstants
import jakarta.inject.Singleton

data class MotherDuckConfiguration(
    val motherduckApiKey: String,
    val destinationPath: String,
    val schema: String,
    val internalTableSchema: String?,
) : DestinationConfiguration()

@Singleton
class MotherDuckConfigurationFactory :
    DestinationConfigurationFactory<MotherDuckSpecification, MotherDuckConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: MotherDuckSpecification
    ): MotherDuckConfiguration {
        return MotherDuckConfiguration(
            motherduckApiKey = pojo.motherduckApiKey,
            destinationPath = pojo.destinationPath,
            schema = pojo.schema,
            internalTableSchema = pojo.internalTableSchema ?: DbConstants.DEFAULT_RAW_TABLE_NAMESPACE
        )
    }
}
