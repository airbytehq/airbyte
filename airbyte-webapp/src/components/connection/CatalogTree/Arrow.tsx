import { faChevronRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React from "react";

import styles from "./Arrow.module.scss";

interface ArrowProps {
  isItemHasChildren?: boolean;
  depth?: number;
  isItemOpen?: boolean;
  onExpand?: () => void;
}

const Arrow: React.FC<ArrowProps> = ({ isItemHasChildren, isItemOpen, onExpand, ...restProps }) => {
  return (
    <span className={styles.container} {...restProps}>
      {(isItemHasChildren || !onExpand) && (
        <FontAwesomeIcon
          icon={faChevronRight}
          onClick={onExpand}
          className={classNames(styles.arrow, { [styles["arrow--rotated"]]: isItemOpen })}
        />
      )}
    </span>
  );
};

export { Arrow };
