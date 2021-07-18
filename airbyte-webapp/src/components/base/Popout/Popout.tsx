import React, { ReactNode } from "react";
import styled from "styled-components";

import { DropDown } from "components";
import { DropdownProps } from "../DropDown";
import { useToggle } from "react-use";

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

const PopupOpener = ({ children, isOpen, target, onClose }: any) => (
  <div css={{ position: "relative" }}>
    {target}
    {isOpen ? <Menu>{children}</Menu> : null}
    {isOpen ? <OutsideClickListener onClick={onClose} /> : null}
  </div>
);

type PopoutProps = DropdownProps & {
  targetComponent: (props: { onOpen: () => void }) => ReactNode;
  onChange: any;
};

const selectStyles = {
  control: (provided: any) => ({ ...provided, minWidth: 240, marginTop: 8 }),
};

const Popout: React.FC<PopoutProps> = ({
  onChange,
  targetComponent,
  ...props
}) => {
  const [isOpen, toggleOpen] = useToggle(false);
  const onSelectChange = (value: any) => {
    toggleOpen();
    onChange(value);
  };

  return (
    <PopupOpener
      isOpen={isOpen}
      onClose={toggleOpen}
      target={targetComponent({ onOpen: toggleOpen })}
    >
      <DropDown
        autoFocus
        backspaceRemovesValue={false}
        components={{
          IndicatorSeparator: null,
          DropdownIndicator: null,
        }}
        controlShouldRenderValue={false}
        hideSelectedOptions={false}
        isClearable={false}
        menuIsOpen
        onChange={onSelectChange}
        options={props.options}
        placeholder={null}
        styles={selectStyles}
        tabSelectsValue={false}
        value={props.value}
      />
    </PopupOpener>
  );
};

export { Popout };
