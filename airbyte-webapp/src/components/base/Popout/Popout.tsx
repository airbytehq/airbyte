import React, { ReactNode } from "react";
import styled from "styled-components";

import { DropDown } from "components";
import { DropdownProps } from "../DropDown";
import { useToggle } from "react-use";
import { ActionMeta } from "react-select";

const OutsideClickListener = styled.div`
  bottom: 0;
  left: 0;
  top: 0;
  right: 0;
  position: fixed;
  z-index: 1;
`;

const Menu = styled.div`
  position: absolute;
  z-index: 2;
`;

type Value = any;

const PopupOpener: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  target: React.ReactNode;
}> = ({ children, isOpen, target, onClose }) => (
  <div css={{ position: "relative" }}>
    {target}
    {isOpen ? <Menu>{children}</Menu> : null}
    {isOpen ? <OutsideClickListener onClick={onClose} /> : null}
  </div>
);

type PopoutProps = DropdownProps & {
  targetComponent: (props: { onOpen: () => void; value: Value }) => ReactNode;
};

const selectStyles = {
  control: (provided: Value) => ({ ...provided, minWidth: 240, marginTop: 8 }),
};

const Popout: React.FC<PopoutProps> = ({
  onChange,
  targetComponent,
  value,
  ...props
}) => {
  const [isOpen, toggleOpen] = useToggle(false);
  const onSelectChange = (value: Value, meta: ActionMeta<Value>) => {
    !props.isMulti && toggleOpen();
    onChange?.(value, meta);
  };

  const components = {
    IndicatorSeparator: null,
    DropdownIndicator: null,
    ...props.components,
  };

  return (
    <PopupOpener
      isOpen={isOpen}
      onClose={toggleOpen}
      target={targetComponent({ onOpen: toggleOpen, value })}
    >
      <DropDown
        autoFocus
        backspaceRemovesValue={false}
        controlShouldRenderValue={false}
        hideSelectedOptions={false}
        isClearable={false}
        menuIsOpen
        placeholder={null}
        styles={selectStyles}
        tabSelectsValue={false}
        {...props}
        onChange={onSelectChange}
        value={value}
        components={components}
      />
    </PopupOpener>
  );
};

export { Popout };
