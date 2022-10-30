import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { useIntl } from "react-intl";
import { components, OptionProps, MenuListProps } from "react-select";
import "/node_modules/flag-icons/css/flag-icons.min.css";

import { DropDown } from "components/ui/DropDown";
import { DropdownProps } from "components/ui/DropDown";

import styles from "./GeographyDropdown.module.scss";

const GeographyOption: React.FC<OptionProps> = (props) => {
  const { formatMessage } = useIntl();
  return (
    <components.Option className={styles.option} {...props}>
      <>
        <span className={`fi fi-${props.label === "auto" ? "us" : props.label}`} />
        <span className={styles.label}>{formatMessage({ id: `geography.${props.label}` })}</span>
      </>
    </components.Option>
  );
};

const MenuList = (props: MenuListProps) => {
  return (
    <components.MenuList {...props}>
      {props.children}
      <div className={styles.menuList}>
        <FontAwesomeIcon icon={faPlus} />
        <span>Request a new geography</span>
      </div>
    </components.MenuList>
  );
};

interface Props<T = unknown> extends DropdownProps {
  options: T[];
  placeholder: string;
}

export const GeographyDropdown: React.FC<Props> = ({ options }) => {
  return (
    <DropDown
      className={styles.reactSelectContainer}
      classNamePrefix="reactSelect"
      options={options}
      components={{ Option: GeographyOption, MenuList }}
    />
  );
};
