import React, { ReactNode, useMemo } from "react";
import styled, { CSSObject } from "styled-components";
import { useToggle } from "react-use";
import { ActionMeta } from "react-select";

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

const Menu = styled.div`
  position: absolute;
  z-index: 2;
`;

type Value = any;

const PopupOpener: React.FC<{
  isOpen: boolean;
  "data-testid"?: string;
  onClose: () => void;
  target: React.ReactNode;
}> = ({ children, isOpen, target, onClose, ...props }) => (
  <div data-testid={props["data-testid"]}>
    {target}
    {isOpen ? <Menu>{children}</Menu> : null}
    {isOpen ? <OutsideClickListener onClick={onClose} /> : null}
  </div>
);

type PopoutProps = DropdownProps & {
  targetComponent: (props: {
    onOpen: () => void;
    isOpen: boolean;
    value: Value;
  }) => ReactNode;
};

const Popout: React.FC<PopoutProps> = ({
  onChange,
  targetComponent,
  ...props
}) => {
  const [isOpen, toggleOpen] = useToggle(false);
  const onSelectChange = (value: Value, meta: ActionMeta<Value>) => {
    !props.isMulti && toggleOpen();
    onChange?.(value, meta);
  };

  const components = useMemo(
    () => ({
      IndicatorSeparator: null,
      DropdownIndicator: null,
      ...props.components,
    }),
    [props.components]
  );

  const selectStyles = {
    control: (provided: Value) => ({
      ...provided,
      minWidth: 240,
      marginTop: 8,
    }),
    menuPortal: (base: CSSObject): CSSObject => ({
      ...base,
      ...(!props.isSearchable ? { transform: "translateY(-37px)" } : {}),
      zIndex: 9999,
    }),
  };

  const target = targetComponent({
    onOpen: toggleOpen,
    isOpen,
    value: props.value,
  });

  return (
    <PopupOpener
      data-testid={props["data-testid"]}
      isOpen={isOpen}
      onClose={toggleOpen}
      target={target}
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
        components={components}
      />
    </PopupOpener>
  );
};

export { Popout };
