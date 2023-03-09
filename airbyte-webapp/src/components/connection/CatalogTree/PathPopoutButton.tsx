import { faCaretDown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";

import { Text } from "components/ui/Text";
import { Tooltip } from "components/ui/Tooltip";

import styles from "./PathPopoutButton.module.scss";

interface PathPopoutButtonProps {
  items?: string[];
  onClick: React.MouseEventHandler;
  testId?: string;
}

export const PathPopoutButton: React.FC<React.PropsWithChildren<PathPopoutButtonProps>> = ({
  items = [],
  onClick,
  children,
  testId,
}) => (
  <Tooltip
    control={
      <button className={styles.button} onClick={onClick} data-testid={testId}>
        <Text size="sm" className={styles.text}>
          {children}
        </Text>
        <FontAwesomeIcon className={styles.arrow} icon={faCaretDown} />
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
