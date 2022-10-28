import React, { ReactNode, useMemo } from "react";
import { ActionMeta, ControlProps, StylesConfig } from "react-select";
import { useToggle } from "react-use";

import { DropDown, DropdownProps } from "components/ui/DropDown";

import { Overlay } from "../Overlay";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Value = any;

const ControlComponent = (props: ControlProps & { selectProps: Value }) => (
  <div ref={props.innerRef}>
    {props.selectProps.selectProps.targetComponent({
      onOpen: props.selectProps.selectProps.onOpen,
      isOpen: props.selectProps.menuIsOpen,
      value: props.selectProps.value,
    })}
  </div>
);

export interface PopoutProps extends DropdownProps {
  targetComponent: (props: { onOpen: () => void; isOpen?: boolean; value: Value }) => ReactNode;
  title?: string;
}

export const Popout: React.FC<PopoutProps> = ({ onChange, targetComponent, ...props }) => {
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

  const selectStyles: StylesConfig = {
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
          onOpen: (e: React.MouseEvent<HTMLButtonElement>) => {
            // Causes a form submit
            e?.preventDefault();
            toggleOpen();
          },
        }}
        backspaceRemovesValue={false}
        controlShouldRenderValue={false}
        hideSelectedOptions={false}
        isClearable={false}
        menuIsOpen={isOpen}
        menuShouldBlockScroll={false}
        placeholder={null}
        tabSelectsValue={false}
        {...props}
        styles={selectStyles}
        onChange={onSelectChange}
        components={components}
      />
      {isOpen && (
        <Overlay
          variant="transparent"
          onClick={(event) => {
            event.stopPropagation();
            toggleOpen();
          }}
        />
      )}
    </>
  );
};
