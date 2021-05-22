import React from "react";
import styled from "styled-components";
import StatusIcon from "components/StatusIcon";
import Status from "core/statuses";

type IProps = {
  id: string;
  lightMode?: boolean;
  name: string | React.ReactNode;
  onClick?: (id: string) => void;
  isActive?: boolean;
  num: number;
  status?: string;
};

const StepView = styled.div<{
  isActive?: boolean;
  lightMode?: boolean;
  nonClickable?: boolean;
}>`
  width: ${({ lightMode }) => (lightMode ? "auto" : "212px")};
  min-width: ${({ lightMode }) => (lightMode ? "100px" : "auto")};
  min-height: 28px;
  padding: 6px 14px;
  border-radius: 4px;
  pointer-events: ${({ isActive, nonClickable }) =>
    isActive || nonClickable ? "none" : "all"};
  cursor: ${({ nonClickable }) => (nonClickable ? "default" : "pointer")};
  text-align: center;
  background: ${({ theme, isActive }) =>
    isActive ? theme.primaryColor12 : "none"};
  color: ${({ theme, isActive }) =>
    isActive ? theme.primaryColor : theme.greyColor60};
  font-weight: 500;
  font-size: 14px;
  line-height: 15px;
  transition: 0.3s;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
`;

const Num = styled.div<{ isActive?: boolean }>`
  width: 16px;
  height: 16px;
  border-radius: 50%;
  text-align: center;
  background: ${({ theme, isActive }) =>
    isActive ? theme.primaryColor : theme.greyColor60};
  color: ${({ theme }) => theme.whiteColor};
  font-weight: 500;
  font-size: 12px;
  line-height: 16px;
  display: inline-block;
  margin-right: 6px;
  box-shadow: 0 1px 2px 0 ${({ theme }) => theme.shadowColor};
`;

const Step: React.FC<IProps> = ({
  name,
  id,
  isActive,
  onClick,
  num,
  lightMode,
  status,
}) => {
  const onItemClickItem = () => {
    if (onClick) {
      onClick(id);
    }
  };

  return (
    <StepView
      data-id={`${id.toLowerCase()}-step`}
      nonClickable={!onClick}
      onClick={onItemClickItem}
      isActive={isActive}
      lightMode={lightMode}
    >
      {lightMode ? null : <Num isActive={isActive}>{num}</Num>}
      {status ? <StatusIcon success={status !== Status.FAILED} /> : null}
      {name}
    </StepView>
  );
};

export default Step;
