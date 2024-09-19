/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.SourceConfiguration

/** Subtype of [SourceConfiguration] for CDC sources. */
interface CdcSourceConfiguration : SourceConfiguration {}
