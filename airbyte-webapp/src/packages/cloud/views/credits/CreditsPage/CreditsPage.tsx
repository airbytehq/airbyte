import React from "react";
import { FormattedMessage } from "react-intl";

import { HeadTitle } from "components/common/HeadTitle";
import { MainPageWithScroll } from "components/common/MainPageWithScroll";
import { PageHeader } from "components/ui/PageHeader";
import { Spinner } from "components/ui/Spinner";
import { Text } from "components/ui/Text";

import { PageTrackingCodes, useTrackPage } from "hooks/services/Analytics";
import { useExperiment } from "hooks/services/Experiment";
import { useFreeConnectorProgramInfo } from "packages/cloud/components/experiments/FreeConnectorProgram/hooks/useFreeConnectorProgram";
import { LargeEnrollmentCallout } from "packages/cloud/components/experiments/FreeConnectorProgram/LargeEnrollmentCallout";
import { useAuthService } from "packages/cloud/services/auth/AuthService";

import CreditsUsage from "./components/CreditsUsage";
import { EmailVerificationHint } from "./components/EmailVerificationHint";
import RemainingCredits from "./components/RemainingCredits";
import styles from "./CreditsPage.module.scss";

const CreditsPage: React.FC = () => {
  const { emailVerified } = useAuthService();
  useTrackPage(PageTrackingCodes.CREDITS);
  const { data } = useFreeConnectorProgramInfo();
  const isFreeConnectorProgramEnabled = useExperiment("workspace.freeConnectorsProgram.visible", false);
  const showEnrollmentUi = isFreeConnectorProgramEnabled && data?.showEnrollmentUi;

  return (
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: "credits.credits" }]} />}
      pageTitle={<PageHeader title={<FormattedMessage id="credits.credits" />} />}
    >
      <div className={styles.content}>
        {!emailVerified && <EmailVerificationHint className={styles.emailVerificationHint} />}
        <RemainingCredits selfServiceCheckoutEnabled={emailVerified} />
        {/* {showEnrollmentUi &&  */}
        {showEnrollmentUi && <LargeEnrollmentCallout />}
        {/* // } */}
        <React.Suspense
          fallback={
            <div className={styles.creditUsageLoading}>
              <Spinner small />
              <Text>
                <FormattedMessage id="credits.loadingCreditsUsage" />
              </Text>
            </div>
          }
        >
          <CreditsUsage />
        </React.Suspense>
      </div>
    </MainPageWithScroll>
  );
};

export default CreditsPage;
