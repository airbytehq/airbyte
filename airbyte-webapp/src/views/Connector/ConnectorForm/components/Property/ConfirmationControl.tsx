import React, { useRef } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components/ui/Button";

const ComponentContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
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
          <Button size="xs" onClick={onDone} type="button" disabled={disabled}>
            <FormattedMessage id="form.done" />
          </Button>
          <Button size="xs" onClick={onCancel} type="button" variant="secondary" disabled={disabled}>
            <FormattedMessage id="form.cancel" />
          </Button>
        </>
      ) : (
        <Button size="xs" onClick={handleStartEdit} type="button" disabled={disabled}>
          <FormattedMessage id="form.edit" />
        </Button>
      )}
    </ComponentContainer>
  );
};

export default ConfirmationControl;
