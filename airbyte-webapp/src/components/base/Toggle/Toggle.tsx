import React from "react";
import styled from "styled-components";

type ToggleProps = {
  small?: boolean;
} & React.InputHTMLAttributes<HTMLInputElement>;

const Switch = styled.label<{ small?: boolean }>`
  position: relative;
  display: inline-block;
  width: ${({ small }) => (small ? 28 : 42)}px;
  min-width: ${({ small }) => (small ? 28 : 42)}px;
  height: ${({ small }) => (small ? 18 : 24)}px;
`;

const SwitchInput = styled.input`
  opacity: 0;
  width: 0;
  height: 0;
`;

const Slider = styled.span<{ small?: boolean }>`
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: ${({ theme }) => theme.greyColor20};
  transition: 0.3s;
  border-radius: 19px;

  &:before {
    position: absolute;
    z-index: 1;
    content: "";
    height: ${({ small }) => (small ? 16 : 22)}px;
    width: ${({ small }) => (small ? 16 : 22)}px;
    left: 1px;
    top: 1px;
    background: ${({ theme }) => theme.whiteColor};
    transition: 0.3s;
    border-radius: 50%;
  }

  input:checked + &&:before {
    transform: translateX(${({ small }) => (small ? 10 : 18)}px);
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

const Toggle: React.FC<ToggleProps> = (props) => {
  return (
    <Switch small={props.small} onClick={(event: React.SyntheticEvent) => event.stopPropagation()}>
      <SwitchInput type="checkbox" {...props} value={props.value} checked={props.checked || !!props.value} />
      <Slider small={props.small} />
    </Switch>
  );
};

export default Toggle;
