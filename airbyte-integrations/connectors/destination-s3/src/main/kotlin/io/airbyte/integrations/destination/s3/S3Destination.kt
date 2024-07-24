/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
@file : Suppress ( "JAVA_MODULE_DOES_NOT_EXPORT_PACKAGE" )

package io.airbyte.integrations.destination.s3

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.destination.s3.BaseS3Destination
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfigFactory
import io.airbyte.cdk.integrations.destination.s3.StorageProvider
import io.github.oshai.kotlinlogging.KotlinLogging
import jdk.internal.loader.BootLoader
import jdk.internal.loader.ClassLoaders
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.io.OutputStream
import java.util.*

val LOGGER = KotlinLogging.logger {  }
@Suppress("deprecation")
open class S3Destination : BaseS3Destination {
    constructor()

    @VisibleForTesting
    constructor(
        s3DestinationConfigFactory: S3DestinationConfigFactory,
        env: Map<String, String>
    ) : super(s3DestinationConfigFactory, env)


    override fun storageProvider(): StorageProvider {
        return StorageProvider.AWS_S3
    }

    companion object {
        @Throws(Exception::class)
        @JvmStatic
        fun main(args: Array<String>) {
            IntegrationRunner(S3Destination()).run(args)
        }
    }
}
