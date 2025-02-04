
package io.airbyte.cdk.test.fixtures.legacy;

import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * AllowedHosts
 * <p>
 * A connector's allowed hosts.  If present, the platform will limit communication to only hosts which are listed in `AllowedHosts.hosts`.
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "hosts"
})
public class AllowedHosts implements Serializable
{

    /**
     * An array of hosts that this connector can connect to.  AllowedHosts not being present for the source or destination means that access to all hosts is allowed.  An empty list here means that no network access is granted.
     * 
     */
    @JsonProperty("hosts")
    @JsonPropertyDescription("An array of hosts that this connector can connect to.  AllowedHosts not being present for the source or destination means that access to all hosts is allowed.  An empty list here means that no network access is granted.")
    private List<String> hosts = new ArrayList<String>();
    @JsonIgnore
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();
    private final static long serialVersionUID = -5046656680170512501L;

    /**
     * An array of hosts that this connector can connect to.  AllowedHosts not being present for the source or destination means that access to all hosts is allowed.  An empty list here means that no network access is granted.
     * 
     */
    @JsonProperty("hosts")
    public List<String> getHosts() {
        return hosts;
    }

    /**
     * An array of hosts that this connector can connect to.  AllowedHosts not being present for the source or destination means that access to all hosts is allowed.  An empty list here means that no network access is granted.
     * 
     */
    @JsonProperty("hosts")
    public void setHosts(List<String> hosts) {
        this.hosts = hosts;
    }

    public AllowedHosts withHosts(List<String> hosts) {
        this.hosts = hosts;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperty(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    public AllowedHosts withAdditionalProperty(String name, Object value) {
        this.additionalProperties.put(name, value);
        return this;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(AllowedHosts.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("hosts");
        sb.append('=');
        sb.append(((this.hosts == null)?"<null>":this.hosts));
        sb.append(',');
        sb.append("additionalProperties");
        sb.append('=');
        sb.append(((this.additionalProperties == null)?"<null>":this.additionalProperties));
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
        result = ((result* 31)+((this.hosts == null)? 0 :this.hosts.hashCode()));
        result = ((result* 31)+((this.additionalProperties == null)? 0 :this.additionalProperties.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof AllowedHosts) == false) {
            return false;
        }
        AllowedHosts rhs = ((AllowedHosts) other);
        return (((this.hosts == rhs.hosts)||((this.hosts!= null)&&this.hosts.equals(rhs.hosts)))&&((this.additionalProperties == rhs.additionalProperties)||((this.additionalProperties!= null)&&this.additionalProperties.equals(rhs.additionalProperties))));
    }

}
