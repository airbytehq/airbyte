import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useState } from "react";
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
      <div className={styles.flag}>
        <span className={`fi fi-${props.label === "auto" ? "us" : props.label}`} />
      </div>
      <span className={styles.label}>{formatMessage({ id: `geography.${props.label}` })}</span>
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
}

export const GeographyDropdown: React.FC<Props> = ({ options }) => {
  const [option, setOption] = useState();
  const { formatMessage } = useIntl();
  const handleOptionSelect = (e: any) => {
    setOption(e.label);
  };

  const formatOptionLabel = ({ label }: { label: string }) => {
    return (
      <div className={styles.optionLabel}>
        <div className={styles.flag}>
          <span className={`fi fi-${label === "auto" ? "us" : label}`} />
        </div>
        <span className={styles.label}>{formatMessage({ id: `geography.${label}` })}</span>
      </div>
    );
  };

  const customStyles = {
    option: (provided: any, state: any) => ({
      ...provided,
      color: "black",
      backgroundColor: state.isSelected ? "#eae9ff" : "#ffffff",
      borderRadius: "10px",

      "&:hover": {
        backgroundColor: state.isSelected ? "#eae9ff" : "#f8f8fa",
      },
    }),
    valueContainer: () => ({
      display: "flex",
    }),
  };

  return (
    <DropDown
      className={styles.reactSelectContainer}
      classNamePrefix="reactSelect"
      options={options}
      components={{ Option: GeographyOption, MenuList }}
      onChange={handleOptionSelect}
      value={option}
      formatOptionLabel={formatOptionLabel}
      styles={customStyles}
      placeholder="Select a region..."
    />
  );
};
