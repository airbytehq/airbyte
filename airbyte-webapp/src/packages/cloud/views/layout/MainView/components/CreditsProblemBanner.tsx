import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Link } from "components/Link";

import { CloudRoutes } from "packages/cloud/cloudRoutes";
import { CreditStatus } from "packages/cloud/lib/domain/cloudWorkspaces/types";

const Container = styled.div`
  height: 30px;
  width: 100%;
  background: ${({ theme }) => theme.redColor};
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

type CreditsProblemBannerProps = {
  status: CreditStatus;
};

const CreditsProblemBanner: React.FC<CreditsProblemBannerProps> = ({ status }) => (
  <Container>
    <FormattedMessage
      id={`credits.creditsProblem.${status}`}
      values={{ lnk: (content: React.ReactNode) => <CreditsLink to={CloudRoutes.Credits}>{content}</CreditsLink> }}
    />
  </Container>
);

export { CreditsProblemBanner };
