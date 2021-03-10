import React, { useRef } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import { Button, Input, InputProps } from "components";

const InputContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const SmallButton = styled(Button)`
  margin-left: 8px;
  padding: 6px 8px 7px;
`;

type ConfirmationInputProps = InputProps & {
  showButtons?: boolean;
  isEditInProgress?: boolean;
  onStart: () => void;
  onCancel: () => void;
  onDone: () => void;
};

const ConfirmationInput: React.FC<ConfirmationInputProps> = (props) => {
  const inputElement = useRef<HTMLInputElement>(null);
  const { isEditInProgress, showButtons, onStart, onCancel, onDone } = props;

  if (!showButtons) {
    return <Input {...props} />;
  }

  const handleStartEdit = () => {
    if (inputElement && inputElement.current) {
      inputElement.current.removeAttribute("disabled");
      inputElement.current.focus();
    }
    onStart();
  };

  return (
    <InputContainer>
      <Input
        {...props}
        ref={inputElement}
        autoFocus={isEditInProgress}
        disabled={!isEditInProgress}
      />
      {isEditInProgress ? (
        <>
          <SmallButton onClick={onDone} type="button">
            <FormattedMessage id="form.done" />
          </SmallButton>
          <SmallButton onClick={onCancel} type="button" secondary>
            <FormattedMessage id="form.cancel" />
          </SmallButton>
        </>
      ) : (
        <SmallButton onClick={handleStartEdit} type="button">
          <FormattedMessage id="form.edit" />
        </SmallButton>
      )}
    </InputContainer>
  );
};

export default ConfirmationInput;
