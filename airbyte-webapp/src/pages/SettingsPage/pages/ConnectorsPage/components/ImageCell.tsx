import classNames from "classnames";
import React, { PropsWithChildren } from "react";

import { Text } from "components/ui/Text";

import styles from "./ImageCell.module.scss";

interface ImageCellProps {
  imageName: string;
  link: string | undefined;
}

const ImageCellText: React.FC<PropsWithChildren<{ className?: string }>> = ({ children, className }) => (
  <Text size="sm" className={classNames(styles.imageNameText, className)}>
    {children}
  </Text>
);

const ImageCell: React.FC<ImageCellProps> = ({ imageName, link }) => {
  if (!link || !link.length) {
    return <ImageCellText>{imageName}</ImageCellText>;
  }

  return (
    <a href={link} target="_blank" rel="noreferrer" className={styles.linkText}>
      <ImageCellText className={styles.linkText}>{imageName}</ImageCellText>
    </a>
  );
};

export default ImageCell;
