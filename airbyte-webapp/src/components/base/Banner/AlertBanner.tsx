import React from "react";
import { FormattedMessage } from "react-intl";

import { Link } from "components/Link";

import { CloudRoutes } from "packages/cloud/cloudRoutes";
import { CreditStatus } from "packages/cloud/lib/domain/cloudWorkspaces/types";

import styles from "./AlertBanner.module.scss";

interface AlertBannerProps {
  alertTypes: string[];
  id: CreditStatus | string;
}

export const AlertBanner: React.FC<AlertBannerProps> = ({ alertTypes, id }) => {
  let alertToDisplay: string;
  alertTypes.length > 1
    ? (alertToDisplay = alertTypes[0])
    : alertTypes.includes("deleted")
    ? (alertToDisplay = "deleted")
    : alertTypes.includes("credits")
    ? (alertToDisplay = "credits")
    : alertTypes.includes("trial")
    ? (alertToDisplay = "trial")
    : (alertToDisplay = alertTypes[0]);

  return (
    <div
      className={`${styles.alertBannerContainer}, ${
        alertToDisplay === "deleted" ? styles.attentionBackground : styles.beigeBackground
      }`}
    >
      {alertToDisplay === "credits" ? (
        <FormattedMessage
          id={id}
          values={{
            lnk: (content: React.ReactNode) => (
              <Link to={CloudRoutes.Credits} className={styles.blackText}>
                {content}
              </Link>
            ),
          }}
        />
      ) : (
        <FormattedMessage id={id} />
      )}
    </div>
  );
};
