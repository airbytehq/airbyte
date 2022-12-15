/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.featureflag

import com.launchdarkly.sdk.ContextKind
import com.launchdarkly.sdk.LDContext
import com.launchdarkly.sdk.LDUser
import com.launchdarkly.sdk.server.LDClient
import java.nio.file.Path

sealed class Flag(internal val key: String) {
    object FeatureOne : Flag("feature-one")
    object FeatureTwo : Flag("feature-two")
}

data class Workspace(override val key: String) : Context {
    override val kind = "workspace"
}

data class User(override val key: String) : Context {
    override val kind = "user"
}

sealed interface Context {
    val kind: String
    val key: String
}

sealed interface Client {
    fun bool(key: Flag, ctx: Context, default: Boolean): Boolean
}

/**
 * LaunchDarkly v5 version
 *
 * LaunchDarkly v6 introduces LDContext which replaces the LDUser class,
 * however this is only available to early-access users accounts currently.
 *
 * Once v6 is GA, this method would be removed and replaced with toLDContext.
 */
private fun Context.toLDUser(): LDUser {
    return LDUser(key)
}

/**
 * LaunchDarkly v6 version
 *
 * Replaces toLDUser once LaunchDarkly v6 is GA.
 */
private fun Context.toLDContext(): LDContext {
    return LDContext.create(ContextKind.of(kind), key)
}

class LD(sdkKey: String) : Client {
    private val ldClient: LDClient = LDClient(sdkKey)

    override fun bool(flag: Flag, ctx: Context, default: Boolean): Boolean {
        return ldClient.boolVariation(flag.key, ctx.toLDUser(), default)
    }
}

class OSS(config: Path) : Client {
    override fun bool(key: Flag, ctx: Context, default: Boolean): Boolean {
        TODO("Not yet implemented")
    }

}
