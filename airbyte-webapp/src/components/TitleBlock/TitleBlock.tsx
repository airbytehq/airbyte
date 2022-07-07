import React from "react";

import { H5 } from "components";
import ContentCard from "components/ContentCard";

import styles from "./TitleBlock.module.scss";

interface IProps {
  title: React.ReactElement;
  actions: React.ReactElement;
}

const TitleBlock: React.FC<IProps> = ({ title, actions }) => {
  return (
    <ContentCard className={styles.contentCard}>
      <div className={styles.titleContainer}>
        <H5 bold>{title}</H5>
      </div>
      <div>{actions}</div>
    </ContentCard>
  );
};

export default TitleBlock;
