/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql

import io.airbyte.cdk.testutils.ContainerFactory
import org.testcontainers.containers.MySQLContainer
import org.testcontainers.utility.DockerImageName

/** Much like the destination-postgres PostgresTestDatabase, this was copied from source-mysql. */
class MySQLContainerFactory : ContainerFactory<MySQLContainer<*>>() {
    override fun createNewContainer(imageName: DockerImageName?): MySQLContainer<*> {
        return MySQLContainer(imageName?.asCompatibleSubstituteFor("mysql"))
    }
}
