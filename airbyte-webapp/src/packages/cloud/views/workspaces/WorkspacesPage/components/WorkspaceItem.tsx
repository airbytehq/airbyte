import { faChevronRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";

import { H5 } from "components/base/Titles";

import styles from "./WorkspaceItem.module.scss";

const WorkspaceItem: React.FC<React.PropsWithChildren<{ onClick: (id: string) => void; id: string }>> = (props) => (
  <button className={styles.button} onClick={() => props.onClick(props.id)}>
    <H5 bold>{props.children}</H5>
    <FontAwesomeIcon className={styles.iconColor} icon={faChevronRight} />
  </button>
);

export default WorkspaceItem;
