import { faChevronRight, faChevronDown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React, { ReactElement } from "react";
import { useToggle } from "react-use";

import styles from "./CollapsablePanel.module.scss";

const Arrow: React.FC<{ isOpen: boolean }> = ({ isOpen }) => (
  <FontAwesomeIcon icon={isOpen ? faChevronDown : faChevronRight} />
);

/**
 * CollapsablePanel defines a reusable "click to expand" UI element. It has two
 * props for content slots, each containing an arbitrary component tree:
 *   - children: the "above the fold" or "title" content which is always shown
 *   - drawer: the "below the fold" content which is expanded or hidden on user interaction
 *
 * The rationale for putting the "above the fold" content in `children` is that
   react's syntactic sugar for `children` makes the source code better reflect
   the rendered UI, with the always-present content defined inline next to
   its "peer" components in the surrounding context.
 */
export const CollapsablePanel: React.FC<{
  drawer: ReactElement;
  initiallyOpen?: boolean;
  className?: string;
  openClassName?: string;
  closedClassName?: string;
}> = ({ drawer, initiallyOpen = false, children, className, openClassName, closedClassName }) => {
  const [isOpen, toggleOpen] = useToggle(initiallyOpen);
  return (
    <div
      className={classNames({
        [className || ""]: true,
        [openClassName || ""]: isOpen,
        [closedClassName || ""]: !isOpen,
      })}
    >
      <div>
        <button className={styles.arrow} tabIndex={0} onClick={toggleOpen}>
          <Arrow isOpen={isOpen} />
        </button>
        {children}
      </div>
      {isOpen ? drawer : null}
    </div>
  );
};
