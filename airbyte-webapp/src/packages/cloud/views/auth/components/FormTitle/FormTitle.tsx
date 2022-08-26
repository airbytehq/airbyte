import React from "react";

import styles from "./FormTitle.module.scss";

export const FormTitle: React.FC = ({ children }) => <h1 className={styles.title}>{children}</h1>;
