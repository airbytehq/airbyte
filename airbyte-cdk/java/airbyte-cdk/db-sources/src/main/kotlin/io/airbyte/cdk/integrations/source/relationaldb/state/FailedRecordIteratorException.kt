/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

class FailedRecordIteratorException(cause: Throwable?) : RuntimeException(cause)
