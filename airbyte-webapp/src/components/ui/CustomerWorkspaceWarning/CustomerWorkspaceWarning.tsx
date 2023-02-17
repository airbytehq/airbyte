import { FormattedMessage, useIntl } from "react-intl";

import { Text } from "components/ui/Text";

import { useCurrentUser } from "packages/cloud/services/auth/AuthService";
import { useListUsers } from "packages/cloud/services/users/UseUserHook";

import styles from "./CustomerWorkspaceWarning.module.scss";
import { Tooltip } from "../Tooltip";

export const CustomerWorkspaceWarning = () => {
  const user = useCurrentUser();
  const workspaceUsers = useListUsers();
  const { formatMessage } = useIntl();

  if (!workspaceUsers.some((member) => member.userId === user.userId)) {
    return (
      <div className={styles.customerWorkspace}>
        <Tooltip
          placement="right"
          control={<Text inverseColor>{formatMessage({ id: "workspace.customerWorkspaceWarning" })}</Text>}
        >
          <FormattedMessage id="workspace.customerWorkspaceWarningTooltip" />
        </Tooltip>
      </div>
    );
  }

  return null;
};
