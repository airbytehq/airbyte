import React, { useRef, useState } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import { InputProps } from "../types";
import InputView from "./InputView";
import Button from "../../Button";

const InputContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const SmallButton = styled(Button)`
  margin-left: 8px;
  padding: 6px 8px 7px;
`;

const InputWithEditButton: React.FC<InputProps> = props => {
  const [isEditMode, setIsEditMode] = useState(false);
  const inputElement = useRef<HTMLInputElement>(null);

  const onStartEdit = () => {
    setIsEditMode(true);
    if (inputElement && inputElement.current) {
      inputElement.current.removeAttribute("disabled");
      inputElement.current.focus();
    }
    if (props.setValue) {
      props.setValue("");
    }
  };

  return (
    <InputContainer>
      <InputView
        {...props}
        ref={inputElement}
        autoFocus={isEditMode}
        disabled={!isEditMode}
      />
      {isEditMode ? null : (
        <SmallButton onClick={onStartEdit} type="button">
          <FormattedMessage id="form.edit" />
        </SmallButton>
      )}
    </InputContainer>
  );
};

export default InputWithEditButton;
