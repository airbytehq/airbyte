import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { theme } from "theme";

import { Button } from "components";
import { RotateIcon } from "components/icons/RotateIcon";

import { FeatureItem, useFeature } from "hooks/services/Feature";

const ButtonBox = styled(Button)<{ disabled?: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #d1d5db;
  width: 168px;
  height: 46px;
  border-radius: 6px;
  margin-top: 36px;
  color: ${({ theme, disabled }) => (disabled ? theme.grey300 : theme.black300)};
`;

const ButtonInnerContainer = styled.div`
  display: flex;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const RotateIconContainer = styled.div`
  display: flex;
  margin-right: 16px;
`;

interface IProps {
  onSync: () => void;
  disabled?: boolean;
}

const SyncNowButton: React.FC<IProps> = ({ onSync, disabled }) => {
  const allowSync = useFeature(FeatureItem.AllowSync);
  return (
    <ButtonBox disabled={!allowSync || disabled} onClick={onSync} iconOnly>
      <ButtonInnerContainer>
        <RotateIconContainer>
          <RotateIcon color={!allowSync || disabled ? theme.grey300 : theme.primaryColor} />
        </RotateIconContainer>
        <FormattedMessage id="sources.syncNow" />
      </ButtonInnerContainer>
    </ButtonBox>
  );
};

export default SyncNowButton;
