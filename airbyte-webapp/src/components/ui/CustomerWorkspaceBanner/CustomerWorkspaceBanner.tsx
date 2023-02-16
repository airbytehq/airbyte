import { Text } from "components/ui/Text";

import { useCurrentUser } from "packages/cloud/services/auth/AuthService";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";

import styles from "./CustomerWorkspaceBanner.module.scss";

export const CustomerWorkspaceBanner = () => {
  const workspace = useCurrentWorkspace();
  const user = useCurrentUser();
  const airbyteEmail = "@airbyte.io";
  console.log(workspace, user);

  if (user.email.includes(airbyteEmail) && !workspace.email?.includes(airbyteEmail)) {
    return (
      <div className={styles.customerWorkspace}>
        <Text inverseColor>
          Warning - you are viewing a workspace not owned by an @airbyte.io account. Make changes with care!
        </Text>
      </div>
    );
  }

  return null;
};
