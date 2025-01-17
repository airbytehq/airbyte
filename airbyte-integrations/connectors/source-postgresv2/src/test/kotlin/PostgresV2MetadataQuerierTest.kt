package io.airbyte.integrations.source.postgresv2

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.integrations.source.postgresv2.PostgresContainerFactory.exec
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class PostgresV2MetadataQuerierTest {

    val postgres_db = PostgresContainerFactory.shared("postgres:16")

    init {
        postgres_db.exec("CREATE TABLE table1 (id INT PRIMARY KEY, name VARCHAR(200));")
    }

    val pg_querier_factory = PostgresV2MetadataQuerier.Factory(
        selectQueryGenerator = PostgresV2SourceOperations(),
        fieldTypeMapper = PostgresV2SourceOperations(),
        checkQueries = JdbcCheckQueries(),
        constants = DefaultJdbcConstants(),
    )

    @Test
    fun test() {
        val configPojo = PostgresV2SourceConfigurationSpecification().apply {
            port = PostgresContainerFactory.config(postgres_db).port
            host = postgres_db.host
            database = "test"
            username = "test"
            password = "test"
        }
        val config: PostgresV2SourceConfiguration = PostgresV2SourceConfigurationFactory().makeWithoutExceptionHandling(configPojo)
        pg_querier_factory.session(config).streamNamespaces().forEach {
            println(it)
        }
        Assertions.assertEquals(listOf("public"), pg_querier_factory.session(config).streamNamespaces())
        pg_querier_factory.session(config).streamNames("public").forEach {
            println(it)
        }
        Assertions.assertTrue(pg_querier_factory.session(config).streamNames("public").containsAll(listOf(StreamIdentifier("public", "table1"))))
    }



}
