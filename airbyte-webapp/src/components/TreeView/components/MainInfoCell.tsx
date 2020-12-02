import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChevronRight } from "@fortawesome/free-solid-svg-icons";

import { Cell } from "../../SimpleTableComponents";
import CheckBox from "../../CheckBox";

type IProps = {
  label: string;
  hideCheckbox?: boolean;
  isItemHasChildren?: boolean;
  isItemChecked?: boolean;
  isItemOpen?: boolean;
  onExpand: () => void;
  onCheckBoxClick: () => void;
};

const ArrowContainer = styled.span`
  padding: 0 9px 0 18px;
`;

const Arrow = styled(FontAwesomeIcon)<{ isOpen?: boolean }>`
  font-size: 16px;
  line-height: 16px;
  color: ${({ theme }) => theme.darkPrimaryColor};
  transform: ${({ isOpen }) => isOpen && "rotate(90deg)"};
  transition: 0.3s;
  cursor: pointer;
`;

const MainCell = styled(Cell)`
  overflow: hidden;
  text-overflow: ellipsis;
`;

const ItemLable = styled.span`
  font-weight: 500;
  font-size: 15px;
  line-height: 18px;
  padding-left: 9px;
`;

const MainInfoCell: React.FC<IProps> = ({
  isItemChecked,
  isItemHasChildren,
  isItemOpen,
  onExpand,
  onCheckBoxClick,
  label,
  hideCheckbox
}) => {
  return (
    <MainCell flex={2}>
      {isItemHasChildren && (
        <ArrowContainer>
          <Arrow icon={faChevronRight} isOpen={isItemOpen} onClick={onExpand} />
        </ArrowContainer>
      )}
      {!hideCheckbox && (
        <CheckBox checked={isItemChecked} onClick={onCheckBoxClick} />
      )}
      <ItemLable>{label}</ItemLable>
    </MainCell>
  );
};

export default MainInfoCell;
