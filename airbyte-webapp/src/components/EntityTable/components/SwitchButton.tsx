import React from "react";
import styled from "styled-components";

interface IProps {
  id: string;
  checked: boolean;
  onClick?: () => void;
}

const CheckBoxWrapper = styled.div`
  position: relative;
`;
const CheckBoxLabel = styled.label`
  position: absolute;
  top: 0;
  left: 0;
  width: 44px;
  height: 24px;
  border-radius: 15px;
  background: #e5e7eb;
  cursor: pointer;
  &::after {
    content: "";
    display: block;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    margin: 2px 2px 2px 2px;
    background: #ffffff;
    box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.1), 0px 1px 2px rgba(0, 0, 0, 0.06);
    transition: 0.2s;
  }
`;
const CheckBox = styled.input`
  opacity: 0;
  z-index: 1;
  border-radius: 15px;
  width: 44px;
  height: 24px;
  &:checked + ${CheckBoxLabel} {
    background: #4f46e5;
    &::after {
      content: "";
      display: block;
      border-radius: 50%;
      width: 20px;
      height: 20px;
      margin-left: 22px;
      transition: 0.2s;
    }
  }
`;

const SwitchButton: React.FC<IProps> = ({ id, checked, onClick }) => {
  return (
    <CheckBoxWrapper>
      <CheckBox id={id} type="checkbox" checked={checked} onClick={onClick} />
      <CheckBoxLabel htmlFor={id} />
    </CheckBoxWrapper>
  );
};

export default SwitchButton;
