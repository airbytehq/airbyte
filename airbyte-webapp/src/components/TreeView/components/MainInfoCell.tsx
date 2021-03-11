import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChevronRight } from "@fortawesome/free-solid-svg-icons";

import { Cell } from "components/SimpleTableComponents";
import { CheckBox } from "components/CheckBox";

type IProps = {
  label: string;
  hideCheckbox?: boolean;
  isItemHasChildren?: boolean;
  depth?: number;
  isItemChecked?: boolean;
  isItemOpen?: boolean;
  onExpand?: () => void;
  onCheckBoxClick?: () => void;
};

const ArrowContainer = styled.span`
  padding: 0 19px 0 18px;
  width: 10px;
  display: inline-block;
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
`;

const Content = styled.div<{ depth?: number }>`
  overflow: hidden;
  text-overflow: ellipsis;
  padding-left: ${({ depth = 0 }) => depth * 58}px;
`;

const ItemLable = styled.span`
  font-weight: 500;
  font-size: 15px;
  line-height: 18px;
  padding-left: 9px;
  cursor: default;
`;

const MainInfoCell: React.FC<IProps> = ({
  isItemChecked,
  isItemHasChildren,
  isItemOpen,
  onExpand,
  onCheckBoxClick,
  label,
  hideCheckbox,
  depth,
}) => {
  return (
    <MainCell flex={2}>
      <Content depth={depth}>
        {(isItemHasChildren || !depth) && (
          <ArrowContainer>
            {(isItemHasChildren || !onExpand) && (
              <Arrow
                icon={faChevronRight}
                isOpen={isItemOpen}
                onClick={onExpand}
              />
            )}
          </ArrowContainer>
        )}
        {!hideCheckbox && (
          <CheckBox checked={isItemChecked} onClick={onCheckBoxClick} />
        )}
        <ItemLable title={label}>{label}</ItemLable>
      </Content>
    </MainCell>
  );
};

export default MainInfoCell;
