import { Popout, PopoutProps } from "../Popout";
import { Tooltip } from "../Tooltip";
import { PillButton } from "./PillButton";

type PillSelectProps = Pick<PopoutProps, "value" | "options" | "isMulti" | "onChange">;

export const PillSelect: React.FC<PillSelectProps> = (props) => {
  return (
    <Popout
      {...props}
      targetComponent={({ onOpen, isOpen, value }) => {
        const { isMulti } = props;
        const label = isMulti ? value.map(({ label }: { label: string }) => label).join(", ") : value.label;

        return (
          <Tooltip
            control={
              <PillButton onClick={() => onOpen()} active={isOpen}>
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
