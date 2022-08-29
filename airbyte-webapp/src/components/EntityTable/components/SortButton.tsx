import { faCaretDown, faCaretUp } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import * as React from "react";

import { Button } from "components";

import styles from "./SortButton.module.scss";

interface IProps {
  lowToLarge?: boolean;
  wasActive?: boolean;
  onClick: () => void;
}

const SortButton: React.FC<IProps> = ({ wasActive, onClick, lowToLarge }) => {
  return (
    <Button
      customStyle={classNames(styles.sortButtonView, {
        [styles.wasActive]: wasActive,
      })}
      size="xs"
      wasActive={wasActive}
      onClick={onClick}
      icon={<FontAwesomeIcon icon={lowToLarge || !wasActive ? faCaretUp : faCaretDown} />}
    />
  );
};

export default SortButton;
