import React from "react";
import classNames from "classnames";

import styles from "./Card.module.scss";

import { H5 } from "../Titles";

export interface CardProps {
  title?: React.ReactNode;
  fullWidth?: boolean;
  lightPadding?: boolean;
  withPadding?: boolean;
  roundedBottom?: boolean;
}

// const cardStyleByWidth = {
//   fullWidth: styles.fullWidth,
// };

export const Card: React.FC<CardProps> = ({ children, title, fullWidth, lightPadding, withPadding, roundedBottom }) => {
  return (
    <div
      className={classNames(
        styles.container,
        fullWidth ? styles.fullWidth : undefined,
        withPadding ? styles.withPadding : undefined
      )}
    >
      {title ? (
        <H5
          className={classNames(
            styles.title,
            lightPadding || !children ? styles.lightPadding : undefined,
            roundedBottom ? styles.roundedBottom : undefined
          )}
        >
          {title}
        </H5>
      ) : null}
      {children}
    </div>
  );
};

// className={classNames(styles.card, size ? cardStyleBySize[size] : undefined)}

// export const Card = styled.div<{ full?: boolean; $withPadding?: boolean }>`
//   width: ${({ full }) => (full ? "100%" : "auto")};
//   background: ${({ theme }) => theme.whiteColor};
//   border-radius: 10px;
//   box-shadow: 0 2px 4px ${({ theme }) => theme.cardShadowColor};
//   padding: ${({ $withPadding }) => ($withPadding ? "20px" : undefined)};
//   //border: 1px solid ${({ theme }) => theme.greyColor20};
// `;
