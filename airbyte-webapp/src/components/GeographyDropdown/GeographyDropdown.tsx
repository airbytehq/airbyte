import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useState } from "react";
import { useIntl } from "react-intl";
import { components, OptionProps, MenuListProps, StylesConfig } from "react-select";

import "/node_modules/flag-icons/css/flag-icons.min.css";

import { DropDown } from "components/ui/DropDown";
import { DropdownProps } from "components/ui/DropDown";

import { Geography } from "core/request/AirbyteClient";
import { theme } from "packages/cloud/theme";

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
  const { formatMessage } = useIntl();
  return (
    <components.MenuList {...props}>
      {props.children}
      <div className={styles.menuList}>
        <FontAwesomeIcon icon={faPlus} />
        <span>{formatMessage({ id: "geography.new" })}</span>
      </div>
    </components.MenuList>
  );
};

interface GeographySelectOption {
  label: Geography;
  value: Geography;
}

export const GeographyDropdown: React.FC<DropdownProps<GeographySelectOption>> = ({ options }) => {
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

  const customStyles: StylesConfig<GeographySelectOption> = {
    option: (base, state) => {
      let backgroundColor = theme.white;
      const color = theme.black;
      const borderRadius = "10px";

      if (state.isSelected) {
        backgroundColor = theme.blue50;
      }

      if (state.isFocused) {
        backgroundColor = theme.grey50;
      }

      if (state.isFocused && state.isSelected) {
        backgroundColor = theme.blue50;
      }

      return {
        ...base,
        backgroundColor,
        color,
        borderRadius,
      };
    },
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
