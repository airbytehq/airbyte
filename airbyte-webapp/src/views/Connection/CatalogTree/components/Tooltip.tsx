import React from "react";
import styled from "styled-components";

const TooltipContainer = styled.div`
  background: ${({ theme }) => theme.textColor90};
  box-shadow: 0 24px 38px rgba(53, 53, 66, 0.14), 0 9px 46px rgba(53, 53, 66, 0.12), 0 11px 15px rgba(53, 53, 66, 0.2);
  border-radius: 4px;
  padding: 5px 8px 3px;
  font-weight: 500;
  font-size: 11px;
  line-height: 13px;
  color: ${({ theme }) => theme.greyColor0};
  min-width: 100%;
  z-index: 2;
  position: absolute;
  top: 20px;
  display: none;

  div:hover > & {
    display: block;
  }
`;

interface TooltipProps {
  items?: string[];
  className?: string;
}

const Tooltip: React.FC<TooltipProps> = ({ items = [], className }) => {
  if (items.length === 0) {
    return null;
  }

  return (
    <TooltipContainer className={className}>
      {items.map((value, key) => (
        <div key={`tooltip-item-${key}`}>
          {value}
          {key < items.length - 1 ? "," : null}
        </div>
      ))}
    </TooltipContainer>
  );
};

export default Tooltip;
