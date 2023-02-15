import { PropsWithChildren } from "react";

import styles from "./MenuContent.module.scss";

export const MenuContent: React.FC<PropsWithChildren<unknown>> = ({ children }) => {
  return (
    <ul className={styles.menuContent}>
      {Array.isArray(children) ? (
        children.map((child, index) => {
          return <li key={index}>{child}</li>;
        })
      ) : (
        <li>{children}</li>
      )}
    </ul>
  );
};
