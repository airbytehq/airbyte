import { faChevronRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React, { useState } from "react";

import { Card } from "components/ui/Card";
import { Heading } from "components/ui/Heading";

import styles from "./Section.module.scss";

export interface SectionProps {
  title?: React.ReactNode;
  flush?: boolean;
  className?: string;
  collapsible?: boolean;
  collapsedPreviewInfo?: React.ReactNode;
  collapsedInitially?: boolean;
}

export const Section: React.FC<React.PropsWithChildren<SectionProps>> = ({
  title,
  flush,
  children,
  className,
  collapsible = false,
  collapsedPreviewInfo,
  collapsedInitially = false,
}) => {
  const [isCollapsed, setIsCollapsed] = useState(collapsedInitially);

  return (
    <Card>
      <div className={classNames(styles.section, { [styles.flush]: flush }, className)}>
        <div className={styles.header}>
          {title && (
            <Heading as="h2" size="sm">
              {title}
            </Heading>
          )}
          {collapsible && (
            <FontAwesomeIcon
              className={classNames(styles.arrow, { [styles.collapsed]: isCollapsed })}
              icon={faChevronRight}
              onClick={() => setIsCollapsed((prevState) => !prevState)}
              data-testid="section-expand-arrow"
            />
          )}
        </div>
        {isCollapsed && collapsedPreviewInfo}
        {collapsible ? !isCollapsed && children : children}
      </div>
    </Card>
  );
};
