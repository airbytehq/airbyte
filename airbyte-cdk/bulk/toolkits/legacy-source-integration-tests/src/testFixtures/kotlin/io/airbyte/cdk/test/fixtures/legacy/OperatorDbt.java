
package io.airbyte.cdk.test.fixtures.legacy;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import java.io.Serializable;

/**
 * OperatorDbt
 * <p>
 * Settings for a DBT operator
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "gitRepoUrl",
    "gitRepoBranch",
    "dockerImage",
    "dbtArguments"
})
public class OperatorDbt implements Serializable
{

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("gitRepoUrl")
    private String gitRepoUrl;
    @JsonProperty("gitRepoBranch")
    private String gitRepoBranch;
    @JsonProperty("dockerImage")
    private String dockerImage;
    @JsonProperty("dbtArguments")
    private String dbtArguments;
    private final static long serialVersionUID = -7209541719419873639L;

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("gitRepoUrl")
    public String getGitRepoUrl() {
        return gitRepoUrl;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("gitRepoUrl")
    public void setGitRepoUrl(String gitRepoUrl) {
        this.gitRepoUrl = gitRepoUrl;
    }

    public OperatorDbt withGitRepoUrl(String gitRepoUrl) {
        this.gitRepoUrl = gitRepoUrl;
        return this;
    }

    @JsonProperty("gitRepoBranch")
    public String getGitRepoBranch() {
        return gitRepoBranch;
    }

    @JsonProperty("gitRepoBranch")
    public void setGitRepoBranch(String gitRepoBranch) {
        this.gitRepoBranch = gitRepoBranch;
    }

    public OperatorDbt withGitRepoBranch(String gitRepoBranch) {
        this.gitRepoBranch = gitRepoBranch;
        return this;
    }

    @JsonProperty("dockerImage")
    public String getDockerImage() {
        return dockerImage;
    }

    @JsonProperty("dockerImage")
    public void setDockerImage(String dockerImage) {
        this.dockerImage = dockerImage;
    }

    public OperatorDbt withDockerImage(String dockerImage) {
        this.dockerImage = dockerImage;
        return this;
    }

    @JsonProperty("dbtArguments")
    public String getDbtArguments() {
        return dbtArguments;
    }

    @JsonProperty("dbtArguments")
    public void setDbtArguments(String dbtArguments) {
        this.dbtArguments = dbtArguments;
    }

    public OperatorDbt withDbtArguments(String dbtArguments) {
        this.dbtArguments = dbtArguments;
        return this;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(OperatorDbt.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("gitRepoUrl");
        sb.append('=');
        sb.append(((this.gitRepoUrl == null)?"<null>":this.gitRepoUrl));
        sb.append(',');
        sb.append("gitRepoBranch");
        sb.append('=');
        sb.append(((this.gitRepoBranch == null)?"<null>":this.gitRepoBranch));
        sb.append(',');
        sb.append("dockerImage");
        sb.append('=');
        sb.append(((this.dockerImage == null)?"<null>":this.dockerImage));
        sb.append(',');
        sb.append("dbtArguments");
        sb.append('=');
        sb.append(((this.dbtArguments == null)?"<null>":this.dbtArguments));
        sb.append(',');
        if (sb.charAt((sb.length()- 1)) == ',') {
            sb.setCharAt((sb.length()- 1), ']');
        } else {
            sb.append(']');
        }
        return sb.toString();
    }

    @Override
    public int hashCode() {
        int result = 1;
        result = ((result* 31)+((this.gitRepoBranch == null)? 0 :this.gitRepoBranch.hashCode()));
        result = ((result* 31)+((this.dockerImage == null)? 0 :this.dockerImage.hashCode()));
        result = ((result* 31)+((this.dbtArguments == null)? 0 :this.dbtArguments.hashCode()));
        result = ((result* 31)+((this.gitRepoUrl == null)? 0 :this.gitRepoUrl.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof OperatorDbt) == false) {
            return false;
        }
        OperatorDbt rhs = ((OperatorDbt) other);
        return (((((this.gitRepoBranch == rhs.gitRepoBranch)||((this.gitRepoBranch!= null)&&this.gitRepoBranch.equals(rhs.gitRepoBranch)))&&((this.dockerImage == rhs.dockerImage)||((this.dockerImage!= null)&&this.dockerImage.equals(rhs.dockerImage))))&&((this.dbtArguments == rhs.dbtArguments)||((this.dbtArguments!= null)&&this.dbtArguments.equals(rhs.dbtArguments))))&&((this.gitRepoUrl == rhs.gitRepoUrl)||((this.gitRepoUrl!= null)&&this.gitRepoUrl.equals(rhs.gitRepoUrl))));
    }

}
