import { faAngleDown, faAngleRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import styles from "./BuilderOptional.module.scss";

export const BuilderOptional: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div className={styles.wrapper}>
      <button
        type="button"
        onClick={() => {
          setIsOpen(!isOpen);
        }}
        className={classNames(styles.label, { [styles.closed]: !isOpen })}
      >
        {isOpen ? <FontAwesomeIcon icon={faAngleDown} /> : <FontAwesomeIcon icon={faAngleRight} />}
        <FormattedMessage id="connectorBuilder.optionalFieldsLabel" />
      </button>
      {isOpen && <div className={styles.container}>{children}</div>}
    </div>
  );
};
