import classnames from "classnames";
import React from "react";

import { getIcon } from "utils/imageUtils";

import styles from "./ImageBlock.module.scss";

interface ImageBlockProps {
  img?: string;
  num?: number;
  small?: boolean;
  color?: string;
  light?: boolean;
}

export const ImageBlock: React.FC<ImageBlockProps> = ({ img, num, small, color, light }) => {
  const imageCircleClassnames = classnames({
    [styles.circle]: num,
    [styles.iconContainer]: !num || num === undefined,
    [styles.small]: small && !num,
    [styles.darkBlue]: !small && num && !color,
    [styles.green]: color === "green",
    [styles.red]: color === "red",
    [styles.blue]: color === "blue",
    [styles.light]: light,
  });

  const numberStyles = classnames(styles.number, { [styles.light]: light });

  return (
    <div className={imageCircleClassnames}>
      {num ? <div className={numberStyles}>{num}</div> : <div className={styles.icon}>{getIcon(img)}</div>}
    </div>
  );
};

export default ImageBlock;
