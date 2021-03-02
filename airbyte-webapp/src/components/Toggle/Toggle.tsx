import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheck } from "@fortawesome/free-solid-svg-icons";

const Switch = styled.label`
  position: relative;
  display: inline-block;
  width: 60px;
  min-width: 60px;
  height: 30px;
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
  background: ${({ theme }) => theme.lightPrimaryColor};
  transition: 0.3s;
  border-radius: 19px;

  &:before {
    position: absolute;
    z-index: 1;
    content: "";
    height: 24px;
    width: 24px;
    left: 3px;
    bottom: 3px;
    top: 3px;
    background: ${({ theme }) => theme.whiteColor};
    transition: 0.3s;
    border-radius: 50%;

    input:checked + & {
      transform: translateX(30px);
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

const SuccessIcon = styled(FontAwesomeIcon)`
  font-size: 14px;
  line-height: 14px;
  color: ${({ theme }) => theme.whiteColor};
  position: absolute;
  top: 8px;
  left: 8px;
  cursor: pointer;
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
      <SuccessIcon icon={faCheck} />
    </Switch>
  );
};

export default Toggle;
