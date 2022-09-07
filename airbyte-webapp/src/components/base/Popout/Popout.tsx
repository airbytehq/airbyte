import React, { ReactNode, useMemo } from "react";
import { ActionMeta, ControlProps } from "react-select";
import { useToggle } from "react-use";
import styled from "styled-components";

import { DropDown } from "components";
import { DropdownProps } from "components/base/DropDown";

const OutsideClickListener = styled.div`
  bottom: 0;
  left: 0;
  top: 0;
  right: 0;
  position: fixed;
  z-index: 1;
`;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Value = any;

const ControlComponent = (props: ControlProps<Value, false>) => (
  <div ref={props.innerRef}>
    {props.selectProps.selectProps.targetComponent({
      onOpen: props.selectProps.selectProps.onOpen,
      isOpen: props.selectProps.menuIsOpen,
      value: props.selectProps.value,
    })}
  </div>
);

interface PopoutProps extends DropdownProps {
  targetComponent: (props: { onOpen: () => void; isOpen?: boolean; value: Value }) => ReactNode;
}

const Popout: React.FC<PopoutProps> = ({ onChange, targetComponent, ...props }) => {
  const [isOpen, toggleOpen] = useToggle(false);

  const onSelectChange = (value: Value, meta: ActionMeta<Value>) => {
    !props.isMulti && toggleOpen();
    onChange?.(value, meta);
  };

  const components = useMemo(
    () => ({
      IndicatorSeparator: null,
      DropdownIndicator: null,
      Control: ControlComponent,
      ...props.components,
    }),
    [props.components]
  );

  const selectStyles = {
    ...(props.styles ?? {}),
    control: (provided: Value) => ({
      ...provided,
      minWidth: 240,
      marginTop: 8,
    }),
  };

  return (
    <>
      <DropDown
        selectProps={{
          targetComponent,
          onOpen: toggleOpen,
        }}
        backspaceRemovesValue={false}
        controlShouldRenderValue={false}
        hideSelectedOptions={false}
        isClearable={false}
        menuIsOpen={isOpen}
        // menuPosition={"fixed"}
        placeholder={null}
        tabSelectsValue={false}
        {...props}
        styles={selectStyles}
        onChange={onSelectChange}
        components={components}
      />
      {isOpen ? <OutsideClickListener onClick={toggleOpen} /> : null}
    </>
  );
};

export { Popout };
