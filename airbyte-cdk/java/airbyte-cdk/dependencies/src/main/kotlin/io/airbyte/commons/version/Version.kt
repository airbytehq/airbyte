/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.version

import com.fasterxml.jackson.databind.annotation.JsonDeserialize
import com.fasterxml.jackson.databind.annotation.JsonSerialize
import com.google.common.base.Preconditions
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import java.util.*

/** A semVer Version class that allows "dev" as a version. */
@JsonDeserialize(using = VersionDeserializer::class)
@JsonSerialize(using = VersionSerializer::class)
open class Version {
    // We really should have 2 private subtypes: One for dev, and one for standard version, where
    // all the fields are non nullable
    val version: String
    val major: String?
    val minor: String?
    val patch: String?

    constructor(version: String) {
        Preconditions.checkNotNull(version)
        this.version = version
        val parsedVersion =
            version
                .replace("\n", "")
                .trim()
                .split("-".toRegex())
                .dropLastWhile { it.isEmpty() }
                .toTypedArray()[0]
                .split("\\.".toRegex())
                .dropLastWhile { it.isEmpty() }
                .toTypedArray()

        if (isDev) {
            this.major = null
            this.minor = null
            this.patch = null
        } else {
            Preconditions.checkArgument(parsedVersion.size >= 3, "Invalid version string: $version")
            this.major = parsedVersion[0]
            this.minor = parsedVersion[1]
            this.patch = parsedVersion[2]
        }
    }

    constructor(major: String?, minor: String?, patch: String?) {
        this.version = String.format("%s.%s.%s", major, minor, patch)
        this.major = major
        this.minor = minor
        this.patch = patch
    }

    fun serialize(): String {
        return version
    }

    /**
     * Compares two Version to check if they are equivalent.
     *
     * Only the major and minor part of the Version is taken into account.
     */
    fun compatibleVersionCompareTo(another: Version): Int {
        if (isDev || another.isDev) return 0
        val majorDiff = compareVersion(major!!, another.major!!)
        if (majorDiff != 0) {
            return majorDiff
        }
        return compareVersion(minor!!, another.minor!!)
    }

    /** @return true if this is greater than other. otherwise false. */
    fun greaterThan(other: Version): Boolean {
        return patchVersionCompareTo(other) > 0
    }

    /** @return true if this is greater than or equal toother. otherwise false. */
    fun greaterThanOrEqualTo(other: Version): Boolean {
        return patchVersionCompareTo(other) >= 0
    }

    /** @return true if this is less than other. otherwise false. */
    fun lessThan(other: Version): Boolean {
        return patchVersionCompareTo(other) < 0
    }

    /** Compares two Version to check if they are equivalent (including patch version). */
    fun patchVersionCompareTo(another: Version): Int {
        if (isDev || another.isDev) {
            return 0
        }
        val majorDiff = compareVersion(major!!, another.major!!)
        if (majorDiff != 0) {
            return majorDiff
        }
        val minorDiff = compareVersion(minor!!, another.minor!!)
        if (minorDiff != 0) {
            return minorDiff
        }
        return compareVersion(patch!!, another.patch!!)
    }

    /** Compares two Version to check if only the patch version was updated. */
    fun checkOnlyPatchVersionIsUpdatedComparedTo(another: Version): Boolean {
        if (isDev || another.isDev) {
            return false
        }
        val majorDiff = compareVersion(major!!, another.major!!)
        if (majorDiff > 0) {
            return false
        }
        val minorDiff = compareVersion(minor!!, another.minor!!)
        if (minorDiff > 0) {
            return false
        }
        return compareVersion(patch!!, another.patch!!) > 0
    }

    val isDev: Boolean
        get() = version.startsWith(DEV_VERSION_PREFIX)

    override fun toString(): String {
        return "Version{" +
            "version='" +
            version +
            '\'' +
            ", major='" +
            major +
            '\'' +
            ", minor='" +
            minor +
            '\'' +
            ", patch='" +
            patch +
            '\'' +
            '}'
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) {
            return true
        }
        if (other == null || javaClass != other.javaClass) {
            return false
        }
        val that = other as Version
        return version == that.version &&
            major == that.major &&
            minor == that.minor &&
            patch == that.patch
    }

    override fun hashCode(): Int {
        return Objects.hash(version, major, minor, patch)
    }

    companion object {
        const val DEV_VERSION_PREFIX: String = "dev"

        /**
         * Version string needs to be converted to integer for comparison, because string comparison
         * does not handle version string with different digits correctly. For example:
         * `"11".compare("3") < 0`, while `Integer.compare(11, 3) > 0`.
         */
        @SuppressFBWarnings(
            "NP_NULL_PARAM_DEREF"
        ) // We really should have 2 different subtypes of version, one for dev, and for standard
        // versions
        private fun compareVersion(v1: String?, v2: String?): Int {
            return Integer.compare(v1!!.toInt(), v2!!.toInt())
        }

        fun isCompatible(v1: Version, v2: Version): Boolean {
            return v1.compatibleVersionCompareTo(v2) == 0
        }
    }
}
