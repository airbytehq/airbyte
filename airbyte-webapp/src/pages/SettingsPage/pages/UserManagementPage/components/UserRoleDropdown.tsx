import React, { useEffect, useState } from "react";

import { DropDown, DropDownRow } from "components";

import { ROLES } from "core/Constants/roles";

interface IProps {
  value: string;
  options: DropDownRow.IDataItem[];
  onChange?: (option: DropDownRow.IDataItem) => void;
}

const UserRoleDropDown: React.FC<IProps> = ({ value, options, onChange }) => {
  const [selectedRole, setSelectedRole] = useState<string | undefined>();

  useEffect(() => {
    setSelectedRole(value);
  }, [value]);

  const onChangeRole = (option: DropDownRow.IDataItem) => {
    setSelectedRole(option.value);
    onChange?.(option);
  };

  if (selectedRole === ROLES.Administrator_Owner) {
    return <DropDown isDisabled $withBorder $transparentBackground placeholder={selectedRole} />;
  }
  return (
    <DropDown
      isDisabled={selectedRole === ROLES.Administrator_Owner ? true : false}
      $withBorder
      $transparentBackground
      isSearchable
      options={options}
      value={selectedRole}
      onChange={(option: DropDownRow.IDataItem) => onChangeRole(option)}
    />
  );
};

export default UserRoleDropDown;
