import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { H3 } from "components/base";

const Header = styled.div`
  color: ${({ theme }) => theme.whiteColor};
  padding: 59px 78px 39px;
  background: ${({ theme }) => theme.textColor} url("/stars-background.svg");
  max-width: 492px;
  border-radius: 10px 10px 0 0;
  position: relative;
`;

const Rocket = styled.img`
  position: absolute;
  width: 218px;
  transform: matrix(0.99, 0.12, -0.12, 0.99, 0, 0) rotate(-4.78deg);
  top: -54px;
  left: calc(50% - 261px / 2 + 24px);
  transition: 0.8s;
`;

const ModalHeader: React.FC = () => {
  return (
    <Header>
      <H3 center bold parentColor>
        <FormattedMessage id="onboarding.syncCompleted" />
      </H3>
      <Rocket src="/rocket.png" />
    </Header>
  );
};

export default ModalHeader;
