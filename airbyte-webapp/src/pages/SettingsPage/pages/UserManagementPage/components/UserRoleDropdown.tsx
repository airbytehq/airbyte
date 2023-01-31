import React, { useEffect, useState } from "react";

import { DropDown, DropDownRow } from "components";

import { getRoleAgainstRoleNumber, ROLES } from "core/Constants/roles";

interface IProps {
  value: number;
  options: DropDownRow.IDataItem[];
  onChange?: (option: DropDownRow.IDataItem) => void;
  name?: string;
}

const UserRoleDropDown: React.FC<IProps> = ({ value, options, onChange, name }) => {
  const [selectedRole, setSelectedRole] = useState<number | undefined>();

  useEffect(() => {
    setSelectedRole(value);
  }, [value]);

  const onChangeRole = (option: DropDownRow.IDataItem) => {
    // setSelectedRole(option.value);
    onChange?.(option);
  };

  if (getRoleAgainstRoleNumber(selectedRole as number) === ROLES.Administrator_Owner) {
    return (
      <DropDown
        isDisabled
        $withBorder
        $background="white"
        placeholder={getRoleAgainstRoleNumber(selectedRole as number)}
      />
    );
  }
  return (
    <DropDown
      isDisabled={getRoleAgainstRoleNumber(selectedRole as number) === ROLES.Administrator_Owner ? true : false}
      $withBorder
      $background="white"
      // isSearchable
      options={options}
      value={selectedRole}
      onChange={(option: DropDownRow.IDataItem) => onChangeRole(option)}
      name={name}
    />
  );
};

export default UserRoleDropDown;
