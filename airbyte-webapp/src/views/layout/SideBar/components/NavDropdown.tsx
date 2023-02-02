import classNames from "classnames";

import { DropdownMenu, DropdownMenuOptionType } from "components/ui/DropdownMenu";

import styles from "./NavDropdown.module.scss";

interface NavDropdownProps {
  options: DropdownMenuOptionType[];
  label: React.ReactNode;
  icon: React.ReactNode;
  onChange?: (data: DropdownMenuOptionType) => false | void;
}

// todo: we actually can't use as button here on navItem!
export const NavDropdown: React.FC<NavDropdownProps> = ({ options, icon, label, onChange }) => {
  return (
    <DropdownMenu placement="right" displacement={10} options={options} onChange={onChange}>
      {({ open }) => (
        <button className={classNames(styles.dropdownMenuButton, { [styles.open]: open })}>
          {icon}
          {label}
          {/* <NavItem as="div" label={label} icon={icon} to="null" /> */}
        </button>
      )}
    </DropdownMenu>
  );
};
