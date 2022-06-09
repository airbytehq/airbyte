import { faCaretDown, faCaretUp } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import * as React from "react";
import styled from "styled-components";

import { Button } from "components";

const SortButtonView = styled(Button)<{ wasActive?: boolean }>`
  min-width: 18px;
  font-size: 11px;
  line-height: 12px;
  opacity: ${({ wasActive }) => (wasActive ? 1 : 0.4)};
  pointer-events: all;
  background: none;
  border: none;
  color: inherit;
  padding: 0;

  &:hover {
    color: inherit;
  }
`;

interface IProps {
  lowToLarge?: boolean;
  wasActive?: boolean;
  onClick: () => void;
}

const SortButton: React.FC<IProps> = ({ wasActive, onClick, lowToLarge }) => {
  return (
    <SortButtonView wasActive={wasActive} onClick={onClick} iconOnly>
      <FontAwesomeIcon icon={lowToLarge || !wasActive ? faCaretUp : faCaretDown} />
    </SortButtonView>
  );
};

export default SortButton;
