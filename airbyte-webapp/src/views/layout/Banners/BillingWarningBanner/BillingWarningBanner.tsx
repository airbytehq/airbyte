import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";

import styles from "../banners.module.scss";

interface IProps {
  onBillingPage: () => void;
}

const Banner = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 0 7%;
`;

const TextContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-start;
`;

const Text = styled.div`
  font-weight: 500;
  font-size: 13px;
  line-height: 24px;
  color: ${({ theme }) => theme.white};
`;

export const BillingWarningBanner: React.FC<IProps> = ({ onBillingPage }) => {
  return (
    <Banner className={styles.banner}>
      <TextContainer>
        <Text>
          <FormattedMessage id="billing.warning.banner.text1" />
        </Text>
        <Text>
          <FormattedMessage id="billing.warning.banner.text2" />
        </Text>
      </TextContainer>
      <Button size="m" black onClick={onBillingPage}>
        <FormattedMessage id="upgrade.plan.btn" />
      </Button>
    </Banner>
  );
};
