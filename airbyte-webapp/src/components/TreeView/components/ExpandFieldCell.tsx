import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCaretDown } from "@fortawesome/free-solid-svg-icons";
import styled from "styled-components";
import Tooltip from "./Tooltip";

const Content = styled.div`
  font-style: normal;
  font-weight: normal;
  font-size: 10px;
  cursor: pointer;
  position: relative;
`;

const Arrow = styled(FontAwesomeIcon)<{ isOpen?: boolean }>`
  color: ${({ theme }) => theme.greyColor40};
  font-size: 14px;
  margin-left: 6px;
  transform: ${({ isOpen }) => isOpen && "rotate(180deg)"};
  transition: 0.3s;
  vertical-align: sub;
`;

type ExpandFieldCellProps = {
  isItemOpen?: boolean;
  onExpand?: () => void;
  tooltipItems?: string[];
};

const ExpandFieldCell: React.FC<ExpandFieldCellProps> = ({
  onExpand,
  children,
  isItemOpen,
  tooltipItems,
}) => {
  return (
    <Content onClick={onExpand}>
      {children} <Arrow icon={faCaretDown} isOpen={isItemOpen} />
      {tooltipItems && tooltipItems.length ? (
        <Tooltip items={tooltipItems} />
      ) : null}
    </Content>
  );
};

export default ExpandFieldCell;
