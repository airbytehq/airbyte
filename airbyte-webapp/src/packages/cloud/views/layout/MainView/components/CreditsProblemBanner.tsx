import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import { CreditStatus } from "packages/cloud/lib/domain/cloudWorkspaces/types";
import { Link } from "components/Link";
import { CloudRoutes } from "packages/cloud/cloudRoutes";

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
  margin-left: 8px;
`;

type CreditsProblemBannerProps = {
  status: CreditStatus;
};

const CreditsProblemBanner: React.FC<CreditsProblemBannerProps> = ({
  status,
}) => (
  <Container>
    <FormattedMessage id={`credits.creditsProblem.${status}`} />
    <CreditsLink to={CloudRoutes.Credits}>
      <FormattedMessage id="credits.creditsProblem.link" />
    </CreditsLink>
  </Container>
);

export { CreditsProblemBanner };
