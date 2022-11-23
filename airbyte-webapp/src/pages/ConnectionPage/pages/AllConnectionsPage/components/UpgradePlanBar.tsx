import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";

const Container = styled.div`
  width: 100%;
  height: 90px;
  background-color: #9596a4;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
`;

const Text = styled.div`
  font-weight: 500;
  font-size: 16px;
  line-height: 24px;
  display: flex;
  align-items: center;
  color: #ffffff;
  margin-right: 50px;
`;

export const UpgradePlanBar: React.FC = () => {
  return (
    <Container>
      <Text>
        <FormattedMessage id="upgrade.plan.countdown" />
      </Text>
      <Button size="lg" black>
        <FormattedMessage id="upgrade.plan.btn" />
      </Button>
    </Container>
  );
};
