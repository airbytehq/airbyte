import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import { CreditStatus } from "packages/cloud/lib/domain/cloudWorkspaces/types";

const Container = styled.div`
  height: 30px;
  width: 100%;
  background: ${({ theme }) => theme.redColor};
  color: ${({ theme }) => theme.whiteColor};
  text-align: center;
  position: fixed;
  z-index: 3;
  font-size: 12px;
  line-height: 30px;
`;

type CreditsProblemBannerProps = {
  status: CreditStatus;
};

const CreditsProblemBanner: React.FC<CreditsProblemBannerProps> = ({
  status,
}) => (
  <Container>
    <FormattedMessage id={`credits.creditsProblem.${status}`} />
  </Container>
);

export { CreditsProblemBanner };
