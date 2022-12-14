/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.featureflag

import com.launchdarkly.sdk.*;
import com.launchdarkly.sdk.server.*;

data class User(override val key: String) : Context {
    override val kind: String = "user";
}

interface Context {
    val kind: String
    val key: String
}

sealed interface Client {
    fun bool(key: String, ctx: Context, default: Boolean): Boolean
    fun int(key: String, ctx: Context, default: Int): Int
    fun string(key: String, ctx: Context, default: String): String
}

class LD(private val key: String) : Client {
    private val ldClient = LDClient(key)

    override

    fun bool(key: String, ctx: Context, default: Boolean): Boolean {
        TODO("Not yet implemented")
    }

    override fun int(key: String, ctx: Context, default: Int): Int {
        TODO("Not yet implemented")
    }

    override fun string(key: String, ctx: Context, default: String): String {
        TODO("Not yet implemented")
    }
}
