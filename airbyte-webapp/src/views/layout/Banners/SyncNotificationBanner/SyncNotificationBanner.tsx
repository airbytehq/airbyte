import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import styles from "../banners.module.scss";
import { IgnoreNotificationModal } from "./components/IgnoreNotificationModal";
import { CrossIcon } from "./icons/crossIcon";

interface IProps {
  usagePercentage: number;
  onBillingPage: () => void;
}

const Banner = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const Text = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  font-size: 13px;
  line-height: 24px;
  color: ${({ theme }) => theme.white};
`;

const CrossBtn = styled.button`
    cursor: pointer;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    border none;
    padding: 0;
`;

export const SyncNotificationBanner: React.FC<IProps> = ({ usagePercentage, onBillingPage }) => {
  const [ignoreModal, setIgnoreModal] = useState<boolean>(false);

  return (
    <>
      <Banner className={styles.banner}>
        <Text>
          <FormattedMessage id="usage.notification.banner.usageText" values={{ percentage: usagePercentage }} />
        </Text>
        <CrossBtn onClick={() => setIgnoreModal(true)}>
          <CrossIcon />
        </CrossBtn>
      </Banner>
      {ignoreModal && <IgnoreNotificationModal onClose={() => setIgnoreModal(false)} onBillingPage={onBillingPage} />}
    </>
  );
};
