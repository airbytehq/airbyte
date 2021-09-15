package io.airbyte.config.persistence.split_secrets;

import java.util.Objects;
import java.util.UUID;

public class GsmSecretCoordinate {

    private final UUID workspaceId;
    private final UUID secretId;

    // todo: Should the version be exposed here? WHat should this look like for OAuth secrets?
    // todo: Should everything use the smae persistence interface with the config writing?
    public GsmSecretCoordinate(final UUID workspaceId, final UUID secretId) {
        this.workspaceId = workspaceId;
        this.secretId = secretId;
    }

    @Override
    public String toString() {
        return "workspace_" + workspaceId + "_secret_" + secretId;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        GsmSecretCoordinate that = (GsmSecretCoordinate) o;
        return toString().equals(that.toString());
    }

    @Override
    public int hashCode() {
        return Objects.hash(toString());
    }
}
