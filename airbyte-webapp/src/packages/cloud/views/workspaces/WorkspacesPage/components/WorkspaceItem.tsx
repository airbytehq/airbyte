import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChevronRight } from "@fortawesome/free-solid-svg-icons";

import { H5, ContentCard } from "components";

const Item = styled(ContentCard)`
  padding: 20px 28px 20px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  cursor: pointer;
`;

const Arrow = styled(FontAwesomeIcon)`
  color: ${({ theme }) => theme.primaryColor};
`;

const WorkspaceItem: React.FC<{ onClick: (id: string) => void; id: string }> = (
  props
) => {
  return (
    <Item onClick={() => props.onClick(props.id)}>
      <H5 bold>{props.children}</H5>
      <Arrow icon={faChevronRight} />
    </Item>
  );
};

export default WorkspaceItem;
