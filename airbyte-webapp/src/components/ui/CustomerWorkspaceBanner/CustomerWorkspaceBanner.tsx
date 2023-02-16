import { useIntl } from "react-intl";

import { Text } from "components/ui/Text";

import { useCurrentUser } from "packages/cloud/services/auth/AuthService";
import { useListUsers } from "packages/cloud/services/users/UseUserHook";

import styles from "./CustomerWorkspaceBanner.module.scss";

export const CustomerWorkspaceBanner = () => {
  const user = useCurrentUser();
  const workspaceUsers = useListUsers();
  const { formatMessage } = useIntl();

  if (!workspaceUsers.some((member) => member.userId === user.userId)) {
    return (
      <div className={styles.customerWorkspace}>
        <Text inverseColor>{formatMessage({ id: "workspace.customerWorkspaceWarning" })}</Text>
      </div>
    );
  }

  return null;
};
