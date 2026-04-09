/*
 * TBD: Full checker implementation pending — see PR #76168.
 *
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.check

import io.airbyte.cdk.load.check.DestinationChecker
import jakarta.inject.Singleton

/**
 * Redshift connection checker placeholder.
 *
 * TBD: Will validate the full S3 staging → COPY → Redshift pipeline.
 */
@Singleton
class RedshiftChecker : DestinationChecker {
    override fun check() {
        // TBD: implement connection validation
    }

    override fun cleanup() {
        // TBD: implement cleanup
    }
}
