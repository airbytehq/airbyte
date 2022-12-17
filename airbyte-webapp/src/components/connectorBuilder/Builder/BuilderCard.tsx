import classNames from "classnames";
import React from "react";

import { Card } from "components/ui/Card";

import styles from "./BuilderCard.module.scss";

interface BuilderCardProps {
  className?: string;
}

export const BuilderCard: React.FC<React.PropsWithChildren<BuilderCardProps>> = ({ children, className }) => {
  return <Card className={classNames(className, styles.card)}>{children}</Card>;
};
