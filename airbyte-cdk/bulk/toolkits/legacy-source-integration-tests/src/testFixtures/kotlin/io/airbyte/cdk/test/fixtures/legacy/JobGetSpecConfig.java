
package io.airbyte.cdk.test.fixtures.legacy;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import java.io.Serializable;

/**
 * JobGetSpecConfig
 * <p>
 * job check get spec
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "dockerImage",
    "isCustomConnector"
})
public class JobGetSpecConfig implements Serializable
{

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("dockerImage")
    private String dockerImage;
    /**
     * determine if the running image is a custom connector.
     * 
     */
    @JsonProperty("isCustomConnector")
    @JsonPropertyDescription("determine if the running image is a custom connector.")
    private Boolean isCustomConnector;
    private final static long serialVersionUID = 1959664576657927959L;

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("dockerImage")
    public String getDockerImage() {
        return dockerImage;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("dockerImage")
    public void setDockerImage(String dockerImage) {
        this.dockerImage = dockerImage;
    }

    public JobGetSpecConfig withDockerImage(String dockerImage) {
        this.dockerImage = dockerImage;
        return this;
    }

    /**
     * determine if the running image is a custom connector.
     * 
     */
    @JsonProperty("isCustomConnector")
    public Boolean getIsCustomConnector() {
        return isCustomConnector;
    }

    /**
     * determine if the running image is a custom connector.
     * 
     */
    @JsonProperty("isCustomConnector")
    public void setIsCustomConnector(Boolean isCustomConnector) {
        this.isCustomConnector = isCustomConnector;
    }

    public JobGetSpecConfig withIsCustomConnector(Boolean isCustomConnector) {
        this.isCustomConnector = isCustomConnector;
        return this;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(JobGetSpecConfig.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("dockerImage");
        sb.append('=');
        sb.append(((this.dockerImage == null)?"<null>":this.dockerImage));
        sb.append(',');
        sb.append("isCustomConnector");
        sb.append('=');
        sb.append(((this.isCustomConnector == null)?"<null>":this.isCustomConnector));
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
        result = ((result* 31)+((this.isCustomConnector == null)? 0 :this.isCustomConnector.hashCode()));
        result = ((result* 31)+((this.dockerImage == null)? 0 :this.dockerImage.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof JobGetSpecConfig) == false) {
            return false;
        }
        JobGetSpecConfig rhs = ((JobGetSpecConfig) other);
        return (((this.isCustomConnector == rhs.isCustomConnector)||((this.isCustomConnector!= null)&&this.isCustomConnector.equals(rhs.isCustomConnector)))&&((this.dockerImage == rhs.dockerImage)||((this.dockerImage!= null)&&this.dockerImage.equals(rhs.dockerImage))));
    }

}
