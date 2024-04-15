/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.typing_deduping

import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.RawOnlySqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.StreamId.Companion.concatenateRawTableName
import io.airbyte.integrations.destination.mysql.MySQLNameTransformer

class MysqlSqlGenerator : RawOnlySqlGenerator(MySQLNameTransformer()) {

    override fun buildStreamId(
        namespace: String,
        name: String,
        rawNamespaceOverride: String
    ): StreamId {
        return StreamId(
            namingTransformer.getNamespace(namespace),
            namingTransformer.convertStreamName(name),
            namingTransformer.getNamespace(rawNamespaceOverride),
            // The default implementation is just convertStreamName(concatenate()).
            // Wrap in getIdentifier to also truncate.
            // This is probably only necessary because the mysql name transformer
            // doesn't call convertStreamName in getIdentifier (probably a bug?).
            // But that entire NameTransformer interface is a hot mess anyway.
            namingTransformer.getIdentifier(
                namingTransformer.convertStreamName(
                    concatenateRawTableName(namespace, name),
                ),
            ),
            namespace,
            name,
        )
    }
}
