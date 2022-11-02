import { Popout, PopoutProps } from "../Popout";
import { Tooltip } from "../Tooltip";
import { PillButton } from "./PillButton";

type PillSelectProps = Pick<PopoutProps, "value" | "options" | "isMulti" | "onChange" | "className">;

export const PillSelect: React.FC<PillSelectProps> = ({ className, ...props }) => {
  const { isMulti } = props;

  return (
    <Popout
      {...props}
      targetComponent={({ onOpen, isOpen, value }) => {
        const label = value
          ? isMulti
            ? value.map(({ label }: { label: string }) => label).join(", ")
            : value.label
          : "";

        return (
          <Tooltip
            control={
              <PillButton
                onClick={(event) => {
                  event.stopPropagation();
                  onOpen();
                }}
                active={isOpen}
                className={className}
              >
                {label}
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
