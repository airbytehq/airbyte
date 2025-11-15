package io.airbyte.integrations.destination.mysql.check

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.integrations.destination.mysql.spec.MySQLConfiguration
import jakarta.inject.Singleton
import kotlinx.coroutines.runBlocking
import java.time.Clock
import javax.sql.DataSource

@Singleton
class MySQLChecker(
    private val dataSource: DataSource,
    clock: Clock,
) : DestinationChecker<MySQLConfiguration> {

    private val tableName = "_airbyte_check_table_${clock.millis()}"

    override fun check(config: MySQLConfiguration) {
        runBlocking {
            dataSource.connection.use { connection ->
                connection.createStatement().use { statement ->
                    // Create simple test table
                    statement.execute("""
                        CREATE TABLE IF NOT EXISTS `${config.database}`.`$tableName` (
                            test INT
                        )
                    """)

                    // Insert test data
                    statement.execute("""
                        INSERT INTO `${config.database}`.`$tableName` (test)
                        VALUES (42)
                    """)

                    // Verify read
                    val rs = statement.executeQuery("""
                        SELECT COUNT(*) AS count FROM `${config.database}`.`$tableName`
                    """)

                    require(rs.next() && rs.getLong("count") == 1L) {
                        "Failed to verify test data in check table"
                    }
                }
            }
        }
    }

    override fun cleanup(config: MySQLConfiguration) {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement.execute("DROP TABLE IF EXISTS `${config.database}`.`$tableName`")
            }
        }
    }
}
