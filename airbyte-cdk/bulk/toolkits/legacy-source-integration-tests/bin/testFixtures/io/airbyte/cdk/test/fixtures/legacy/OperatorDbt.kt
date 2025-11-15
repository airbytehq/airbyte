/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.annotation.JsonInclude
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import java.io.Serializable

/**
 * OperatorDbt
 *
 * Settings for a DBT operator
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder("gitRepoUrl", "gitRepoBranch", "dockerImage", "dbtArguments")
class OperatorDbt : Serializable {
    /**
     *
     * (Required)
     */
    /**
     *
     * (Required)
     */
    /**
     *
     * (Required)
     */
    @get:JsonProperty("gitRepoUrl")
    @set:JsonProperty("gitRepoUrl")
    @JsonProperty("gitRepoUrl")
    var gitRepoUrl: String? = null

    @get:JsonProperty("gitRepoBranch")
    @set:JsonProperty("gitRepoBranch")
    @JsonProperty("gitRepoBranch")
    var gitRepoBranch: String? = null

    @get:JsonProperty("dockerImage")
    @set:JsonProperty("dockerImage")
    @JsonProperty("dockerImage")
    var dockerImage: String? = null

    @get:JsonProperty("dbtArguments")
    @set:JsonProperty("dbtArguments")
    @JsonProperty("dbtArguments")
    var dbtArguments: String? = null

    fun withGitRepoUrl(gitRepoUrl: String?): OperatorDbt {
        this.gitRepoUrl = gitRepoUrl
        return this
    }

    fun withGitRepoBranch(gitRepoBranch: String?): OperatorDbt {
        this.gitRepoBranch = gitRepoBranch
        return this
    }

    fun withDockerImage(dockerImage: String?): OperatorDbt {
        this.dockerImage = dockerImage
        return this
    }

    fun withDbtArguments(dbtArguments: String?): OperatorDbt {
        this.dbtArguments = dbtArguments
        return this
    }

    override fun toString(): String {
        val sb = StringBuilder()
        sb.append(OperatorDbt::class.java.name)
            .append('@')
            .append(Integer.toHexString(System.identityHashCode(this)))
            .append('[')
        sb.append("gitRepoUrl")
        sb.append('=')
        sb.append((if ((this.gitRepoUrl == null)) "<null>" else this.gitRepoUrl))
        sb.append(',')
        sb.append("gitRepoBranch")
        sb.append('=')
        sb.append((if ((this.gitRepoBranch == null)) "<null>" else this.gitRepoBranch))
        sb.append(',')
        sb.append("dockerImage")
        sb.append('=')
        sb.append((if ((this.dockerImage == null)) "<null>" else this.dockerImage))
        sb.append(',')
        sb.append("dbtArguments")
        sb.append('=')
        sb.append((if ((this.dbtArguments == null)) "<null>" else this.dbtArguments))
        sb.append(',')
        if (sb[sb.length - 1] == ',') {
            sb.setCharAt((sb.length - 1), ']')
        } else {
            sb.append(']')
        }
        return sb.toString()
    }

    override fun hashCode(): Int {
        var result = 1
        result =
            ((result * 31) + (if ((this.gitRepoBranch == null)) 0 else gitRepoBranch.hashCode()))
        result = ((result * 31) + (if ((this.dockerImage == null)) 0 else dockerImage.hashCode()))
        result = ((result * 31) + (if ((this.dbtArguments == null)) 0 else dbtArguments.hashCode()))
        result = ((result * 31) + (if ((this.gitRepoUrl == null)) 0 else gitRepoUrl.hashCode()))
        return result
    }

    override fun equals(other: Any?): Boolean {
        if (other === this) {
            return true
        }
        if ((other is OperatorDbt) == false) {
            return false
        }
        val rhs = other
        return (((((this.gitRepoBranch === rhs.gitRepoBranch) ||
            ((this.gitRepoBranch != null) && (this.gitRepoBranch == rhs.gitRepoBranch))) &&
            ((this.dockerImage === rhs.dockerImage) ||
                ((this.dockerImage != null) && (this.dockerImage == rhs.dockerImage)))) &&
            ((this.dbtArguments === rhs.dbtArguments) ||
                ((this.dbtArguments != null) && (this.dbtArguments == rhs.dbtArguments)))) &&
            ((this.gitRepoUrl === rhs.gitRepoUrl) ||
                ((this.gitRepoUrl != null) && (this.gitRepoUrl == rhs.gitRepoUrl))))
    }

    companion object {
        private const val serialVersionUID = -7209541719419873639L
    }
}
