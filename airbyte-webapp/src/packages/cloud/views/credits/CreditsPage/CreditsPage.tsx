import React from "react";
import { FormattedMessage } from "react-intl";

import { PageTitle } from "components";
import HeadTitle from "components/HeadTitle";
import MainPageWithScroll from "components/MainPageWithScroll";

import { PageTrackingCodes, useTrackPage } from "hooks/services/Analytics";
import { useAuthService } from "packages/cloud/services/auth/AuthService";

import CreditsUsage from "./components/CreditsUsage";
import { EmailVerificationHint } from "./components/EmailVerificationHint";
import RemainingCredits from "./components/RemainingCredits";
import styles from "./CreditsPage.module.scss";

const CreditsPage: React.FC = () => {
  const { emailVerified } = useAuthService();
  useTrackPage(PageTrackingCodes.CREDITS);
  return (
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: "credits.credits" }]} />}
      pageTitle={<PageTitle title={<FormattedMessage id="credits.credits" />} />}
    >
      <div className={styles.content}>
        {!emailVerified && <EmailVerificationHint className={styles.emailVerificationHint} />}
        <RemainingCredits selfServiceCheckoutEnabled={emailVerified} />
        <CreditsUsage />
      </div>
    </MainPageWithScroll>
  );
};

export default CreditsPage;
