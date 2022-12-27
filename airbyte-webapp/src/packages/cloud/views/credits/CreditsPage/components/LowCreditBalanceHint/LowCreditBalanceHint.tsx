import { faCreditCard, faWarning } from "@fortawesome/free-solid-svg-icons";
import { FormattedMessage } from "react-intl";

import { InfoBox } from "components/ui/InfoBox";

import { useGetCloudWorkspace } from "packages/cloud/services/workspaces/CloudWorkspacesService";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";

import styles from "./LowCreditBalanceHint.module.scss";

export const LOW_BALANCE_CREDIT_TRESHOLD = 20;

export const LowCreditBalanceHint: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const workspace = useCurrentWorkspace();
  const cloudWorkspace = useGetCloudWorkspace(workspace.workspaceId);

  if (cloudWorkspace.remainingCredits > LOW_BALANCE_CREDIT_TRESHOLD) {
    return null;
  }

  const status = cloudWorkspace.remainingCredits === 0 ? "zeroBalance" : "lowBalance";

  const ICONS = {
    lowBalance: faCreditCard,
    zeroBalance: faWarning,
  };
  return (
    <InfoBox icon={ICONS[status]} error={status === "zeroBalance"} className={styles.container}>
      <div className={styles.wrapper}>
        <FormattedMessage id={`credits.${status}`} />
        {children}
      </div>
    </InfoBox>
  );
};
