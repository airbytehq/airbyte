import React from "react";

import styles from "./EmptyResourceBlock.module.scss";

interface IEmptyResourceBlockProps {
  text: React.ReactNode;
  description?: React.ReactNode;
}

export const EmptyResourceBlock: React.FC<IEmptyResourceBlockProps> = ({ text, description }) => (
  <div className={styles.content}>
    <div className={styles.imgBlock}>
      <img src="/cactus.png" height={40} alt="cactus" />
    </div>
    {text}
    <div className={styles.description}>{description}</div>
  </div>
);
