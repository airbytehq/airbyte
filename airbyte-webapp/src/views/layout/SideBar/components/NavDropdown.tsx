import classNames from "classnames";

import { DropdownMenu, DropdownMenuOptionType } from "components/ui/DropdownMenu";

import styles from "./NavDropdown.module.scss";
import { NavItem } from "./NavItem";

interface NavDropdownProps {
  options: DropdownMenuOptionType[];
  label: React.ReactNode;
  icon: React.ReactNode;
}

export const NavDropdown: React.FC<NavDropdownProps> = ({ options, icon, label }) => {
  return (
    <DropdownMenu placement="right" displacement={10} options={options}>
      {({ open }) => (
        <NavItem
          as="button"
          label={label}
          icon={icon}
          to="banana" // todo: fix types to fix this
          className={classNames(styles.dropdownMenuButton, { [styles.open]: open })}
        />
      )}
    </DropdownMenu>
  );
};
