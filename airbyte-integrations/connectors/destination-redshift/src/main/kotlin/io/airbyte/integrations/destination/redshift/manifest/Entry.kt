/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift.manifest

class Entry @JvmOverloads constructor(val url: String, val mandatory: Boolean = true)
