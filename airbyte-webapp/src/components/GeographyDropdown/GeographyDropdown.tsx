import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { EU, US } from "country-flag-icons/react/3x2";
import React from "react";
import { useIntl } from "react-intl";
import { components, OptionProps, MenuListProps } from "react-select";

import { DropDown } from "components/ui/DropDown";

import styles from "./GeographyDropdown.module.scss";

const options = [
  {
    value: "en",
    label: "en",
  },
  {
    value: "auto",
    label: "auto",
  },
  {
    value: "eu",
    label: "eu",
  },
];

const flags: Record<string, React.ReactNode> = {
  auto: <US />,
  us: <US />,
  eu: <EU />,
};

const GeographyOption: React.FC<OptionProps> = (props) => {
  const { formatMessage } = useIntl();
  return (
    <components.Option className={styles.option} {...props}>
      <>
        <span className={styles.flag}>{flags[props.label]}</span>
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

export const GeographyDropdown: React.FC = (props) => {
  return (
    <DropDown
      className={styles.reactSelectContainer}
      classNamePrefix="reactSelect"
      options={options}
      components={{ Option: GeographyOption, MenuList }}
    />
  );
};
