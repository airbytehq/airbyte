import { faCreditCard, faWarning } from "@fortawesome/free-solid-svg-icons";
import { FormattedMessage } from "react-intl";

import { InfoBox } from "components/ui/InfoBox";

import { CreditStatus } from "packages/cloud/lib/domain/cloudWorkspaces/types";
import { useGetCloudWorkspace } from "packages/cloud/services/workspaces/CloudWorkspacesService";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";

import styles from "./LowCreditBalanceHint.module.scss";

export const LOW_BALANCE_CREDIT_TRESHOLD = 20;

export const LowCreditBalanceHint: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const workspace = useCurrentWorkspace();
  const cloudWorkspace = useGetCloudWorkspace(workspace.workspaceId);

  const isNoBillingAccount =
    cloudWorkspace.remainingCredits <= 0 && cloudWorkspace.creditStatus === CreditStatus.POSITIVE;
  if (isNoBillingAccount || cloudWorkspace.remainingCredits > LOW_BALANCE_CREDIT_TRESHOLD) {
    return null;
  }

  const status = cloudWorkspace.remainingCredits <= 0 ? "zeroBalance" : "lowBalance";
  const variant = status === "zeroBalance" ? "error" : "default";

  const ICONS = {
    lowBalance: faCreditCard,
    zeroBalance: faWarning,
  };
  return (
    <InfoBox className={styles.container} icon={ICONS[status]} variant={variant}>
      <div className={styles.wrapper}>
        <FormattedMessage id={`credits.${status}`} />
        {children}
      </div>
    </InfoBox>
  );
};
