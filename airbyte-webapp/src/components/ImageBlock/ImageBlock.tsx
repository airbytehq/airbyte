import classnames from "classnames";
import React from "react";

import { getIcon } from "utils/imageUtils";

import styles from "./ImageBlock.module.scss";

interface ImageBlockProps {
  img?: string;
  num?: number;
  small?: boolean;
  color?: string;
}

export const ImageBlock: React.FC<ImageBlockProps> = ({ img, num, small, color }) => {
  const imageCircleClassnames = classnames({
    [styles.circle]: num,
    [styles.iconContainer]: !num || num === undefined,
    [styles.small]: small && !num,
    [styles.darkBlue]: !small && num,
    [styles.green]: color === "green",
    [styles.red]: color === "red",
    [styles.blue]: color === "blue",
  });
  return (
    <div className={imageCircleClassnames}>
      {num ? <div className={styles.number}>{num}</div> : <div className={styles.icon}>{getIcon(img)}</div>}
    </div>
  );
};

export default ImageBlock;
