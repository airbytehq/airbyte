import { EU, US } from "country-flag-icons/react/3x2";
import React from "react";
import { components, OptionProps, MenuListProps } from "react-select";

import { DropDown } from "components/ui/DropDown";

import styles from "./GeographyDropdown.module.scss";

const options = [
  {
    value: "us",
    label: "us",
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
  console.log(props);
  return (
    <components.Option {...props}>
      <>
        <span className={styles.flag}>{flags[props.label]}</span>
        <span className={styles.label}>{props.label}</span>
      </>
    </components.Option>
  );
};

const MenuList = (props: MenuListProps) => {
  return (
    <components.MenuList {...props}>
      {props.children}
      <div>Request a new geography</div>
    </components.MenuList>
  );
};

export const GeographyDropdown: React.FC = () => {
  return <DropDown options={options} defaultValue={options[0]} components={{ Option: GeographyOption, MenuList }} />;
};
