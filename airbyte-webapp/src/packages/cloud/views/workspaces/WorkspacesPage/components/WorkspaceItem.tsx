import { faChevronRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import styled from "styled-components";

import { H5 } from "components";

import styles from "./WorkspaceItem.module.scss";

// const Item = styled(ContentCard)`
//   padding: 20px 28px 20px 20px;
//   display: flex;
//   justify-content: space-between;
//   align-items: center;
//   margin-bottom: 10px;
//   cursor: pointer;
// `;

const Arrow = styled(FontAwesomeIcon)`
  color: ${({ theme }) => theme.primaryColor};
`;

const WorkspaceItem: React.FC<{ onClick: (id: string) => void; id: string }> = (props) => (
  <button className={styles.item} onClick={() => props.onClick(props.id)}>
    <H5 bold>{props.children}</H5>
    <Arrow icon={faChevronRight} />
  </button>
);

export default WorkspaceItem;
