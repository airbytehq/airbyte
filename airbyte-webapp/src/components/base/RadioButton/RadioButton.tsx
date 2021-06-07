import React from "react";
import styled from "styled-components";

const RadioButtonInput = styled.input`
  opacity: 0;
  width: 0;
  height: 0;
  margin: 0;
`;

const Check = styled.div`
  height: 100%;
  width: 100%;
  border-radius: 50%;
  background: ${({ theme }) => theme.primaryColor};
`;

const RadioButtonContainer = styled.label`
  height: 16px;
  width: 16px;
  background: ${({ theme }) => theme.greyColor20};
  color: ${({ theme }) => theme.primaryColor};
  text-align: center;
  border-radius: 50%;
  display: inline-block;
  padding: 4px;
  cursor: pointer;
`;

const RadioButton: React.FC<React.InputHTMLAttributes<HTMLInputElement>> = (
  props
) => {
  return (
    <RadioButtonContainer
      className={props.className}
      onClick={(event: React.SyntheticEvent) => event.stopPropagation()}
    >
      {props.checked && <Check />}
      <RadioButtonInput
        {...props}
        type="radio"
        checked={props.checked}
        onChange={props.onChange}
      />
    </RadioButtonContainer>
  );
};

export default RadioButton;
