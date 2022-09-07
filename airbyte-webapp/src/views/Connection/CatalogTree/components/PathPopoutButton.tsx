import { faSortDown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";

import { Text } from "components/base/Text";
import { Tooltip } from "components/base/Tooltip";

import styles from "./PathPopoutButton.module.scss";

interface PathPopoutButtonProps {
  items?: string[];
  onClick: React.MouseEventHandler;
}

export const PathPopoutButton: React.FC<PathPopoutButtonProps> = ({ items = [], onClick, children }) => (
  <Tooltip
    control={
      <button className={styles.button} onClick={onClick}>
        <Text size="sm" className={styles.text}>
          {children}
        </Text>
        <FontAwesomeIcon className={styles.arrow} icon={faSortDown} />
      </button>
    }
    placement="bottom-start"
    disabled={items.length === 0}
  >
    {items.map((value, key) => (
      <div key={`tooltip-item-${key}`}>
        {value}
        {key < items.length - 1 && ","}
      </div>
    ))}
  </Tooltip>
);
