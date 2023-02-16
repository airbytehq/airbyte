import classNames from "classnames";
import { PropsWithChildren } from "react";

import styles from "./SideBar.module.scss";

export const SideBar: React.FC<PropsWithChildren<unknown>> = ({ children }) => {
  return <nav className={classNames(styles.nav)}>{children}</nav>;
};
