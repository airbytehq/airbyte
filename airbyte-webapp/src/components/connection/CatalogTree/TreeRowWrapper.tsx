import classNames from "classnames";
import React from "react";

import { Row } from "components/SimpleTableComponents";

import styles from "./TreeRowWrapper.module.scss";

const TreeRowWrapper: React.FC<React.PropsWithChildren<{ depth?: number; noBorder?: boolean }>> = ({
  depth,
  children,
  noBorder,
}) => (
  <div
    className={classNames(styles.rowWrapper, {
      [styles["rowWrapper--hasDepth"]]: depth && depth > 0,
      [styles["rowWrapper--noBorder"]]: noBorder,
    })}
  >
    <Row className={styles.rowContent}>{children}</Row>
  </div>
);

export { TreeRowWrapper };
