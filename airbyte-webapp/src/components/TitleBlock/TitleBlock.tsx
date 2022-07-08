import React from "react";

import { H5 } from "components";

import styles from "./TitleBlock.module.scss";

interface IProps {
  title: React.ReactElement;
  actions?: React.ReactElement;
}

const TitleBlock: React.FC<IProps> = ({ title, actions }) => {
  return (
    <div className={styles.titleBlock}>
      <div className={styles.titleContainer}>
        <H5 bold>{title}</H5>
      </div>
      {actions && <div>{actions}</div>}
    </div>
  );
};

export default TitleBlock;
