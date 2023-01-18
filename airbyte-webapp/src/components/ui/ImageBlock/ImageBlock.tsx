import classnames from "classnames";
import React from "react";

import { getIcon } from "utils/imageUtils";

import styles from "./ImageBlock.module.scss";

interface ImageBlockProps {
  img: string;
  small?: boolean;
  "aria-label"?: string;
}

export const ImageBlock: React.FC<ImageBlockProps> = ({ img, small, "aria-label": ariaLabel }) => {
  const imageCircleClassnames = classnames(styles.iconContainer, {
    [styles.small]: small,
  });

  return (
    <div className={imageCircleClassnames} aria-label={ariaLabel}>
      <div className={styles.icon}>{getIcon(img)}</div>
    </div>
  );
};
