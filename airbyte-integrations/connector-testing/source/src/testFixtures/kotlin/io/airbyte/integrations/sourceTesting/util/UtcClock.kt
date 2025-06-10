/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.sourceTesting.util

import jakarta.inject.Singleton
import java.time.Clock

@Singleton fun utcClock(): Clock = Clock.systemUTC()
