import React from "react";
import styled from "styled-components";

interface IProps {
  isActive: boolean;
  onSelect: () => void;
  label?: string;
}

const LabelText = styled.div`
  font-weight: 400;
  font-size: 10px;
  display: flex;
  align-items: center;
  color: #6b6b6f;
  position: absolute;
  top: -20px;
  user-select: none;
`;

const Mark = styled.div<{
  isActive: boolean;
}>`
  width: 18px;
  height: 18px;
  background: ${({ theme, isActive }) => (isActive ? theme.primaryColor : "transparent")};
  border-radius: 25px;
  cursor: pointer;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
`;

const LabelInnerCircle = styled.div`
  width: 8px;
  height: 8px;
  background: ${({ theme }) => theme.white};
  border-radius: 50%;
`;

const SliderMark: React.FC<IProps> = ({ isActive, onSelect, label }) => {
  return (
    <Mark isActive={isActive} onClick={onSelect}>
      <LabelText>{label}</LabelText>
      <LabelInnerCircle />
    </Mark>
  );
};

export default SliderMark;
