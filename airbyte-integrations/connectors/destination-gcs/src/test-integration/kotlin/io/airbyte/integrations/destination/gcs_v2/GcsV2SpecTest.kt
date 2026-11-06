/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import io.airbyte.cdk.load.spec.SpecTest

/** Snapshot test for the generated connector spec. No GCS credentials required. */
class GcsV2SpecTest : SpecTest(additionalMicronautEnvs = GcsV2Destination.additionalMicronautEnvs)
