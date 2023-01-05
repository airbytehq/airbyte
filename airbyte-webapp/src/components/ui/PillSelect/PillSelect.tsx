import React from "react";

import { Popout, PopoutProps } from "../Popout";
import { Tooltip } from "../Tooltip";
import { PillButton, PillButtonVariant } from "./PillButton";

type PickedPopoutProps = Pick<PopoutProps, "value" | "options" | "isMulti" | "onChange" | "className">;

interface PillSelectProps extends PickedPopoutProps {
  variant?: PillButtonVariant;
  disabled?: boolean;
  renderDisabledState?: () => React.ReactNode;
}

export const PillSelect: React.FC<PillSelectProps> = ({ className, renderDisabledState, ...props }) => {
  const { isMulti, variant, disabled } = props;
  return (
    <Popout
      {...props}
      isDisabled={disabled}
      targetComponent={({ onOpen, isOpen, value }) => {
        const label = value
          ? isMulti
            ? value.map(({ label }: { label: string }) => (Array.isArray(label) ? label.join(" | ") : label)).join(", ")
            : value.label
          : "";
        return (
          <Tooltip
            control={
              <PillButton
                variant={variant}
                disabled={disabled}
                onClick={(event) => {
                  event.stopPropagation();
                  onOpen();
                }}
                active={isOpen}
                className={className}
              >
                {disabled && !!renderDisabledState ? renderDisabledState() : label}
              </PillButton>
            }
            placement="bottom-start"
            disabled={isOpen || !isMulti || value?.length <= 1}
          >
            {label}
          </Tooltip>
        );
      }}
    />
  );
};
