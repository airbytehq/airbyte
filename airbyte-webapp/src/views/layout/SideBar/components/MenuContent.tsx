import { PropsWithChildren } from "react";

import styles from "./MenuContent.module.scss";

export const MenuContent: React.FC<PropsWithChildren<{ children: React.ReactNode[] }>> = ({ children }) => {
  return (
    <ul className={styles.menuContent}>
      {children.map((child, index) => {
        return <li key={index}>{child}</li>;
      })}
    </ul>
  );
};
