import React from "react";

import styles from "./Card.module.scss";

import { H5 } from "../Titles";

export interface CardProps {
  title?: React.ReactNode;
  full?: boolean;
}

export const Card: React.FC<CardProps> = ({ children, title }) => {
  return (
    <div className={styles.container}>
      {title ? <H5>{title}</H5> : null}
      {children}
    </div>
  );
};

// <Title light={light || !children} roundedBottom={!!children}>
//         {title}
//       </Title>

// export const Card = styled.div<{ full?: boolean; $withPadding?: boolean }>`
//   width: ${({ full }) => (full ? "100%" : "auto")};
//   background: ${({ theme }) => theme.whiteColor};
//   border-radius: 10px;
//   box-shadow: 0 2px 4px ${({ theme }) => theme.cardShadowColor};
//   padding: ${({ $withPadding }) => ($withPadding ? "20px" : undefined)};
//   //border: 1px solid ${({ theme }) => theme.greyColor20};
// `;
