import React, { useRef } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";

const ComponentContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const SmallButton = styled(Button)`
  margin-left: 8px;
  padding: 6px 8px 7px;
`;

interface ConfirmationControlProps {
  component: React.ReactElement;
  showButtons?: boolean;
  isEditInProgress?: boolean;
  onStart: () => void;
  onCancel: () => void;
  onDone: () => void;
  disabled?: boolean;
}

const ConfirmationControl: React.FC<ConfirmationControlProps> = ({
  isEditInProgress,
  showButtons,
  onStart,
  onCancel,
  onDone,
  component,
  disabled,
}) => {
  const controlRef = useRef<HTMLElement>(null);

  if (!showButtons) {
    return <>{component}</>;
  }

  const handleStartEdit = () => {
    if (controlRef && controlRef.current) {
      controlRef.current?.removeAttribute?.("disabled");
      controlRef.current?.focus?.();
    }
    onStart();
  };

  return (
    <ComponentContainer>
      {React.cloneElement(component, {
        ref: controlRef,
        autoFocus: isEditInProgress,
        disabled: !isEditInProgress || disabled,
      })}
      {isEditInProgress ? (
        <>
          <SmallButton onClick={onDone} type="button" disabled={disabled}>
            <FormattedMessage id="form.done" />
          </SmallButton>
          <SmallButton onClick={onCancel} type="button" secondary disabled={disabled}>
            <FormattedMessage id="form.cancel" />
          </SmallButton>
        </>
      ) : (
        <SmallButton onClick={handleStartEdit} type="button" disabled={disabled}>
          <FormattedMessage id="form.edit" />
        </SmallButton>
      )}
    </ComponentContainer>
  );
};

export default ConfirmationControl;
