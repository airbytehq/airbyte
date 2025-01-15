package io.airbyte.integrations.source.mydb

import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

data class MyDbSourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val jdbcProperties: Map<String, String>,
) : JdbcSourceConfiguration {

    @Factory
    private class MicronautFactory {
        @Singleton
        fun mydbSourceConfig(
            factory: SourceConfigurationFactory<
                MyDbSourceConfigurationSpecification,
                MyDbSourceConfiguration,
                >,
            supplier: ConfigurationSpecificationSupplier<MyDbSourceConfigurationSpecification>,
        ): MyDbSourceConfiguration = factory.make(supplier.get())
    }
}

@Singleton
class MyDbSourceConfigurationFactory :
    SourceConfigurationFactory<
        MyDbSourceConfigurationSpecification, MyDbSourceConfiguration> {
    override fun makeWithoutExceptionHandling(pojo: MyDbSourceConfigurationSpecification): MyDbSourceConfiguration {
        val realHost = pojo.host
        val realPort = pojo.port
        val jdbcProperties = mutableMapOf<String, String>()
        jdbcProperties["user"] = pojo.username
        pojo.password?.let { jdbcProperties["password"] = it }
        return MyDbSourceConfiguration(
            realHost = realHost,
            realPort = realPort,
            jdbcProperties = jdbcProperties,
        )
    }
}
