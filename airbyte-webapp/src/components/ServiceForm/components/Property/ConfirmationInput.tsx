import React, { useRef, useState } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import Input, { InputProps } from "../../../Input";
import Button from "../../../Button";

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
  onStart?: () => void;
  onCancel?: () => void;
  onDone?: () => void;
};

const ConfirmationInput: React.FC<ConfirmationInputProps> = props => {
  const inputElement = useRef<HTMLInputElement>(null);
  const { showButtons, onStart, onCancel, onDone } = props;
  const [isInEditMode, setInEditMode] = useState(false);

  if (!showButtons) {
    return <Input {...props} />;
  }

  const handleStartEdit = () => {
    setInEditMode(true);
    if (inputElement && inputElement.current) {
      inputElement.current.removeAttribute("disabled");
      inputElement.current.focus();
    }
    onStart?.();
  };

  const handleCancel = () => {
    setInEditMode(false);
    onCancel?.();
  };

  const handleDone = () => {
    setInEditMode(false);
    onDone?.();
  };

  return (
    <InputContainer>
      <Input
        {...props}
        ref={inputElement}
        autoFocus={isInEditMode}
        disabled={!isInEditMode}
      />
      {isInEditMode ? (
        <>
          <SmallButton onClick={handleDone} type="button">
            <FormattedMessage id="form.done" />
          </SmallButton>
          <SmallButton onClick={handleCancel} type="button">
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
