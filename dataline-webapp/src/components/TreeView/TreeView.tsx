import React, { useState } from "react";
import CheckboxTree from "react-checkbox-tree";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChevronRight, faCheck } from "@fortawesome/free-solid-svg-icons";

import "react-checkbox-tree/lib/react-checkbox-tree.css";

type INode = {
  value: string;
  label: string;
  children?: Array<INode>;
};

type IProps = {
  nodes: Array<INode>;
  checked?: Array<string>;
  onCheck: (data: string[]) => void;
};

const ArrowContainer = styled.div`
  padding: 0 22px 0 18px;
`;

const Arrow = styled(FontAwesomeIcon)<{ isOpen?: boolean }>`
  font-size: 16px;
  line-height: 16px;
  color: ${({ theme }) => theme.darkPrimaryColor};
  transform: ${({ isOpen }) => !isOpen && "rotate(90deg)"};
  transition: 0.3s;
`;

const CheckBoxContainer = styled.div`
  height: 20px;
  width: 20px;
  background: ${({ theme }) => theme.greyColor20};
  color: ${({ theme }) => theme.primaryColor};
  text-align: center;
  border-radius: 4px;
  font-size: 14px;
  line-height: 14px;
  display: inline-block;
  padding: 2px 0;
`;

const Minus = styled.div`
  height: 3px;
  width: 14px;
  background: ${({ theme }) => theme.primaryColor};
  vertical-align: middle;
`;

const Container = styled.div`
  & .rct-text {
    border-bottom: 1px solid ${({ theme }) => theme.greyColor20};
    height: 40px;
    display: flex;
    align-items: center;
  }

  & .rct-collapse {
    padding: 0;
  }

  & label:active,
  & label:hover {
    background: none;
  }

  & ol ol {
    padding-left: 50px;
  }
`;

const TreeView: React.FC<IProps> = ({ nodes, checked, onCheck }) => {
  const [expanded, setExpanded] = useState<Array<string>>([]);

  return (
    <Container>
      <CheckboxTree
        nodes={nodes}
        checked={checked}
        expanded={expanded}
        onCheck={onCheck}
        onExpand={expandedItem => setExpanded(expandedItem)}
        icons={{
          check: (
            <CheckBoxContainer>
              <FontAwesomeIcon icon={faCheck} />
            </CheckBoxContainer>
          ),
          uncheck: (
            <CheckBoxContainer>
              <span />
            </CheckBoxContainer>
          ),
          halfCheck: (
            <CheckBoxContainer>
              <Minus />
            </CheckBoxContainer>
          ),
          expandClose: (
            <ArrowContainer>
              <Arrow icon={faChevronRight} isOpen />
            </ArrowContainer>
          ),
          expandOpen: (
            <ArrowContainer>
              <Arrow icon={faChevronRight} />
            </ArrowContainer>
          ),
          expandAll: null,
          collapseAll: null,
          parentClose: null,
          parentOpen: null,
          leaf: null
        }}
      />
    </Container>
  );
};

export default TreeView;
