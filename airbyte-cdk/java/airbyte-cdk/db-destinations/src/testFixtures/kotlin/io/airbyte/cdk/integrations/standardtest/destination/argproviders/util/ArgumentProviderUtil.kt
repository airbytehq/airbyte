/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.destination.argproviders.util

import io.airbyte.cdk.integrations.standardtest.destination.ProtocolVersion
import org.junit.jupiter.api.extension.ExtensionContext

object ArgumentProviderUtil {
    private const val PROTOCOL_VERSION_METHOD_NAME = "getProtocolVersion"

    /**
     * This method use
     * [io.airbyte.cdk.integrations.standardtest.destination.ProtocolVersion.getPrefix] to prefix
     * the file name.
     *
     * example:
     *
     * filename.json -> v0/filename.json
     *
     * @param fileName the original file name
     * @param protocolVersion supported protocol version
     * @return filename with protocol version prefix
     */
    fun prefixFileNameByVersion(fileName: String?, protocolVersion: ProtocolVersion): String {
        return String.format("%s/%s", protocolVersion.prefix, fileName)
    }

    /**
     * This method use reflection to get protocol version method from provided test context.
     *
     * NOTE: getProtocolVersion method should be public.
     *
     * @param context the context in which the current test is being executed.
     * @return supported protocol version
     */
    @Throws(Exception::class)
    fun getProtocolVersion(context: ExtensionContext): ProtocolVersion {
        val c = context.requiredTestClass
        // NOTE: Method should be public
        val m = c.getMethod(PROTOCOL_VERSION_METHOD_NAME)
        return m.invoke(c.getDeclaredConstructor().newInstance()) as ProtocolVersion
    }
}
