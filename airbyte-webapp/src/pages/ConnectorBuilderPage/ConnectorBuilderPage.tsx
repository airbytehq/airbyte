import { useState } from "react";

import { ControlLabels } from "components";
import GroupControls from "components/GroupControls";
import { DropDown } from "components/ui/DropDown";

import { ConnectorBuilderStateProvider } from "services/connectorBuilder/ConnectorBuilderStateService";
import { LabelInfo } from "views/Connector/ConnectorForm/components/Property/LabelInfo";

interface Option {
  label: string;
  value: string;
}

const ConnectorBuilderPageInner: React.FC = () => {
  const options: Option[] = [
    { label: "first", value: "first" },
    { label: "second", value: "second" },
    { label: "third", value: "third" },
  ];
  const [selected, setSelected] = useState(options[0].value);
  const label = "Label";
  const description = "Description";

  return (
    <GroupControls
      title={
        <>
          <ControlLabels
            label={label}
            infoTooltipContent={<LabelInfo label={label} description={description} />}
            optional
          />
          <DropDown
            options={options}
            onChange={(newValue) => {
              setSelected(newValue);
            }}
            value={options.find((option) => option.value === selected)}
            name="name"
          />
        </>
      }
    >
      <div>Inside</div>
    </GroupControls>
  );
};

export const ConnectorBuilderPage: React.FC = () => (
  <ConnectorBuilderStateProvider>
    <ConnectorBuilderPageInner />
  </ConnectorBuilderStateProvider>
);
