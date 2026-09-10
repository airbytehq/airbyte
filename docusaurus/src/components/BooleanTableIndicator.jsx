import { faCheck, faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React from "react";

export const BooleanTableIndicator = ({ label, status }) => {
  const isSupported = status === "supported";

  return (
    <span
      className={classNames(
        "boolean-table-indicator",
        isSupported
          ? "boolean-table-indicator--supported"
          : "boolean-table-indicator--unsupported",
      )}
    >
      <FontAwesomeIcon
        aria-hidden="true"
        className="boolean-table-indicator__icon"
        focusable="false"
        icon={isSupported ? faCheck : faXmark}
      />
      <span>{label}</span>
    </span>
  );
};
