import React from "react";

import { PillButton, PillButtonVariant } from "./PillButton";
import { Popout, PopoutProps } from "../Popout";
import { Tooltip } from "../Tooltip";

type PickedPopoutProps = Pick<PopoutProps, "value" | "options" | "isMulti" | "onChange" | "className">;

interface PillSelectProps extends PickedPopoutProps {
  variant?: PillButtonVariant;
  disabled?: boolean;
  disabledLabel?: React.ReactNode;
  hasError?: boolean;
}

export const PillSelect: React.FC<PillSelectProps> = ({ className, disabledLabel, ...props }) => {
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
                hasError={props?.hasError}
              >
                {(disabled && disabledLabel) || label}
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
