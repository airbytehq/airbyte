import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCaretDown } from "@fortawesome/free-solid-svg-icons";
import styled from "styled-components";

const Content = styled.div`
  font-style: normal;
  font-weight: normal;
  font-size: 10px;
  cursor: pointer;
`;

const Arrow = styled(FontAwesomeIcon)<{ isOpen?: boolean }>`
  color: ${({ theme }) => theme.greyColor40};
  font-size: 14px;
  margin-left: 6px;
  transform: ${({ isOpen }) => isOpen && "rotate(180deg)"};
  transition: 0.3s;
  vertical-align: sub;
`;

type IProps = {
  isItemOpen?: boolean;
  children?: React.ReactNode;
  onExpand?: () => void;
};

const ExpandFieldCell: React.FC<IProps> = ({
  onExpand,
  children,
  isItemOpen,
}) => {
  return (
    <Content onClick={onExpand}>
      {children} <Arrow icon={faCaretDown} isOpen={isItemOpen} />
    </Content>
  );
};

export default ExpandFieldCell;
