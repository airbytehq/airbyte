import { faChevronRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import styled from "styled-components";

interface ArrowProps {
  isItemHasChildren?: boolean;
  depth?: number;
  isItemOpen?: boolean;
  onExpand?: () => void;
}

const ArrowContainer = styled.span`
  padding: 0 12px;
  width: 30px;
  display: inline-block;
`;

const ArrowView = styled(FontAwesomeIcon)<{ $isOpen?: boolean }>`
  font-size: 16px;
  line-height: 16px;
  color: ${({ theme }) => theme.darkPrimaryColor};
  transform: ${({ $isOpen }) => $isOpen && "rotate(90deg)"};
  transition: 0.3s;
  cursor: pointer;
`;

const Arrow: React.FC<ArrowProps> = ({ isItemHasChildren, isItemOpen, onExpand }) => {
  return (
    <ArrowContainer>
      {(isItemHasChildren || !onExpand) && <ArrowView icon={faChevronRight} onClick={onExpand} $isOpen={isItemOpen} />}
    </ArrowContainer>
  );
};

export { Arrow };
