import React from "react";

import styles from "./EmptyResourceBlock.module.scss";

interface EmptyResourceBlockProps {
  text: React.ReactNode;
  description?: React.ReactNode;
}

export const EmptyResourceBlock: React.FC<EmptyResourceBlockProps> = ({ text, description }) => (
  <div className={styles.content}>
    <div className={styles.imgBlock}>
      <img src="/cactus.png" height={40} alt="" />
    </div>
    {text}
    <div className={styles.description}>{description}</div>
  </div>
);
