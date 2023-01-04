import classNames from "classnames";
import React from "react";

import { Card } from "components/ui/Card";
import { CheckBox } from "components/ui/CheckBox";

import styles from "./BuilderCard.module.scss";

interface BuilderCardProps {
  className?: string;
  toggleConfig?: {
    label: React.ReactNode;
    toggledOn: boolean;
    onToggle: (newToggleValue: boolean) => void;
  };
}

export const BuilderCard: React.FC<React.PropsWithChildren<BuilderCardProps>> = ({
  children,
  className,
  toggleConfig,
}) => {
  return (
    <Card className={classNames(className, styles.card)}>
      {toggleConfig && (
        <div className={styles.toggleContainer}>
          <CheckBox
            checked={toggleConfig.toggledOn}
            onChange={(event) => {
              toggleConfig.onToggle(event.target.checked);
            }}
          />
          {toggleConfig.label}
        </div>
      )}
      {(!toggleConfig || toggleConfig.toggledOn) && children}
    </Card>
  );
};
