import React, { useEffect, useState } from "react";

import { DropDown, DropDownRow } from "components";

import { getRoleAgainstRoleNumber, ROLES } from "core/Constants/roles";

interface IProps {
  value: number;
  roleDesc?: string;
  options: DropDownRow.IDataItem[];
  onChange?: (option: DropDownRow.IDataItem) => void;
  name?: string;
}

const UserRoleDropDown: React.FC<IProps> = ({ value, roleDesc, options, onChange, name }) => {
  const [selectedRole, setSelectedRole] = useState<number | undefined>();

  useEffect(() => {
    setSelectedRole(value);
  }, [value]);

  const onChangeRole = (option: DropDownRow.IDataItem) => {
    onChange?.(option);
  };

  if (getRoleAgainstRoleNumber(selectedRole as number) === ROLES.Administrator_Owner) {
    return <DropDown isDisabled $withBorder $background="white" placeholder={roleDesc} />;
  }
  return (
    <DropDown
      isDisabled={getRoleAgainstRoleNumber(selectedRole as number) === ROLES.Administrator_Owner ? true : false}
      $withBorder
      $background="white"
      options={options}
      value={selectedRole}
      onChange={(option: DropDownRow.IDataItem) => onChangeRole(option)}
      name={name}
    />
  );
};

export default UserRoleDropDown;
