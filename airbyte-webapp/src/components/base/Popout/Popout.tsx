import React, { ReactNode, useState } from "react";
import { DropDown } from "components";
import { DropdownProps } from "../DropDown";

const D = ({ children, isOpen, target, onClose }: any) => (
  <div>
    {target}
    {isOpen ? children : null}
    {isOpen ? <div onClick={onClose} /> : null}
  </div>
);

type PopoutProps = DropdownProps & {
  targetComponent: (props: { onOpen: () => void }) => ReactNode;
  onChange: any;
};

const Popout: React.FC<PopoutProps> = ({
  onChange,
  targetComponent,
  ...props
}) => {
  const [state, setState] = useState({ isOpen: false, value: undefined });
  const toggleOpen = () => {
    setState((prevState) => ({ ...prevState, isOpen: !prevState.isOpen }));
  };
  const onSelectChange = (value: any) => {
    toggleOpen();
    onChange(value);
  };

  const { isOpen, value } = state;
  return (
    <D
      isOpen={isOpen}
      onClose={toggleOpen}
      target={targetComponent({ onOpen: toggleOpen })}
    >
      <DropDown
        autoFocus
        backspaceRemovesValue={false}
        components={{ IndicatorSeparator: null }}
        controlShouldRenderValue={false}
        hideSelectedOptions={false}
        isClearable={false}
        menuIsOpen
        onChange={onSelectChange}
        options={props.options}
        tabSelectsValue={false}
        value={value}
      />
    </D>
  );
};

export { Popout };
