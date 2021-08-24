import React from "react";
import styled from "styled-components";

const Switch = styled.label`
  position: relative;
  display: inline-block;
  width: 42px;
  min-width: 42px;
  height: 24px;
`;

const SwitchInput = styled.input`
  opacity: 0;
  width: 0;
  height: 0;
`;

const Slider = styled.span`
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: ${({ theme }) => theme.greyColor20};
  transition: 0.3s;
  border-radius: 19px;
  border: 1px solid ${({ theme }) => theme.textColor};

  &:before {
    position: absolute;
    z-index: 1;
    content: "";
    height: 22px;
    width: 22px;
    left: -1px;
    top: -1px;
    background: ${({ theme }) => theme.whiteColor};
    transition: 0.3s;
    border-radius: 50%;
    border: 1px solid ${({ theme }) => theme.textColor};

    input:checked + & {
      transform: translateX(19px);
    }
  }

  input:checked + & {
    background: ${({ theme }) => theme.primaryColor};
  }

  input:checked:disabled + & {
    opacity: 0.5;
  }

  input:disabled + & {
    cursor: auto;
  }
`;

const Toggle: React.FC<React.InputHTMLAttributes<HTMLInputElement>> = (
  props
) => {
  return (
    <Switch onClick={(event: React.SyntheticEvent) => event.stopPropagation()}>
      <SwitchInput
        type="checkbox"
        {...props}
        value={props.value}
        checked={props.checked || !!props.value}
      />
      <Slider />
    </Switch>
  );
};

export default Toggle;
