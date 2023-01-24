import { faRedoAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components/ui/Button";

import styles from "./UpgradeAllButton.module.scss";

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
  disabled: boolean;
}

const UpgradeAllButton: React.FC<UpdateAllButtonProps> = ({ onUpdate, isLoading, hasError, hasSuccess, disabled }) => {
  return (
    <UpdateButtonContent>
      {hasError && (
        <ErrorBlock>
          <FormattedMessage id="form.someError" />
        </ErrorBlock>
      )}
      <Button
        size="xs"
        className={styles.updateButton}
        onClick={onUpdate}
        isLoading={isLoading}
        disabled={disabled}
        icon={hasSuccess ? undefined : <TryArrow icon={faRedoAlt} />}
      >
        {hasSuccess ? <FormattedMessage id="admin.upgraded" /> : <FormattedMessage id="admin.upgradeAll" />}
      </Button>
    </UpdateButtonContent>
  );
};

export default UpgradeAllButton;
