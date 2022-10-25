import { Popout, PopoutProps } from "../Popout";
import { PillButton } from "./PillButton";

type PillSelectProps = Pick<PopoutProps, "value" | "options" | "isMulti" | "onChange">;

export const PillSelect: React.FC<PillSelectProps> = (props) => {
  return (
    <Popout
      {...props}
      targetComponent={({ onOpen, isOpen, value }) => {
        const label = props.isMulti ? value.map(({ label }: { label: string }) => label).join(", ") : value.label;
        return (
          <PillButton onClick={() => onOpen()} active={isOpen}>
            {label}
          </PillButton>
        );
      }}
    />
  );
};
