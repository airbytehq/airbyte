import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { PageTitle } from "components";
import HeadTitle from "components/HeadTitle";
import MainPageWithScroll from "components/MainPageWithScroll";

import { useAuthService } from "packages/cloud/services/auth/AuthService";

import CreditsUsage from "./components/CreditsUsage";
import { EmailVerificationHint } from "./components/EmailVerificationHint";
import RemainingCredits from "./components/RemainingCredits";

const Content = styled.div`
  margin: 0 33px 0 27px;
  height: 100%;
`;

const EmailVerificationHintWithMargin = styled(EmailVerificationHint)`
  margin-bottom: 8px;
`;

const CreditsPage: React.FC = () => {
  const { emailVerified } = useAuthService();

  return (
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: "credits.credits" }]} />}
      pageTitle={<PageTitle title={<FormattedMessage id="credits.credits" />} />}
    >
      <Content>
        {!emailVerified && <EmailVerificationHintWithMargin />}
        <RemainingCredits selfServiceCheckoutEnabled={emailVerified} />
        <CreditsUsage />
      </Content>
    </MainPageWithScroll>
  );
};

export default CreditsPage;
