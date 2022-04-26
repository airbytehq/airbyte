import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Link } from "components/Link";

import { CloudRoutes } from "packages/cloud/cloudRoutes";
import { CreditStatus } from "packages/cloud/lib/domain/cloudWorkspaces/types";

const Container = styled.div<{ errorType?: string }>`
  height: 30px;
  width: 100%;
  background: ${({ errorType, theme }) => (errorType === "credits" ? theme.redColor : theme.warningColor)};
  color: ${({ theme }) => theme.blackColor};
  text-align: center;
  position: fixed;
  z-index: 3;
  font-size: 12px;
  line-height: 30px;
`;
const CreditsLink = styled(Link)`
  color: ${({ theme }) => theme.blackColor};
`;

interface AlertBannerProps {
  alertType: string;
  id: CreditStatus | string;
}

const AlertBanner: React.FC<AlertBannerProps> = ({ alertType: errorType, id }) => (
  <Container errorType={errorType}>
    {/* todo: this can be abstracted a layer further to unify the component */}
    {errorType === "credits" ? (
      <FormattedMessage
        id={id}
        values={{ lnk: (content: React.ReactNode) => <CreditsLink to={CloudRoutes.Credits}>{content}</CreditsLink> }}
      />
    ) : (
      <FormattedMessage id={id} />
    )}
  </Container>
);

export { AlertBanner };
