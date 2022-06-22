import classnames from "classnames";
import React from "react";

import { getIcon } from "utils/imageUtils";

import styles from "./ImageCircle.module.scss";

interface ImageCircleProps {
  img?: string;
  num?: number;
  small?: boolean;
}

const ImageCircle: React.FC<ImageCircleProps> = ({ img, num, small }) => {
  const imageCircleClassnames = classnames({
    [styles.circle]: num,
    [styles.iconContainer]: !num || num === undefined,
    [styles.small]: small && !num,
    [styles.darkBlue]: !small && num,
  });
  return (
    <div className={imageCircleClassnames}>
      {num ? <div className={styles.number}>{num}</div> : <div className={styles.icon}>{getIcon(img)}</div>}
    </div>
  );
};

export default ImageCircle;
export { ImageCircle };
