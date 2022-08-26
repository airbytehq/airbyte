import { faRedoAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { LoadingButton } from "components";

const UpdateButton = styled(LoadingButton)`
  margin: -6px 0;
  min-width: 120px;
`;

const TryArrow = styled(FontAwesomeIcon)`
  margin: 0 10px -1px 0;
  font-size: 14px;
`;

const UpdateButtonContent = styled.div`
  position: relative;
  display: inline-block;
  margin-left: 5px;
`;

const ErrorBlock = styled.div`
  color: ${({ theme }) => theme.dangerColor};
  font-size: 11px;
  position: absolute;
  font-weight: normal;
  bottom: -17px;
  line-height: 11px;
  right: 0;
  left: -46px;
`;

interface UpdateAllButtonProps {
  onUpdate: () => void;
  isLoading: boolean;
  hasError: boolean;
  hasSuccess: boolean;
}

const UpgradeAllButton: React.FC<UpdateAllButtonProps> = ({ onUpdate, isLoading, hasError, hasSuccess }) => {
  return (
    <UpdateButtonContent>
      {hasError && (
        <ErrorBlock>
          <FormattedMessage id="form.someError" />
        </ErrorBlock>
      )}
      <UpdateButton onClick={onUpdate} isLoading={isLoading} wasActive={hasSuccess}>
        {hasSuccess ? (
          <FormattedMessage id="admin.upgraded" />
        ) : (
          <>
            <TryArrow icon={faRedoAlt} />
            <FormattedMessage id="admin.upgradeAll" />
          </>
        )}
      </UpdateButton>
    </UpdateButtonContent>
  );
};

export default UpgradeAllButton;
