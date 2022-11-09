import { ConnectorIcon } from "components/common/ConnectorIcon";

import { Connector, ConnectorDefinition } from "core/domain/connector";
import { ReleaseStage } from "core/request/AirbyteClient";
import { naturalComparator } from "utils/objects";

/**
 * Returns the order for a specific release stage label. This will define
 * in what order the different release stages are shown inside the select.
 * They will be shown in an increasing order (i.e. 0 on top), unless not overwritten
 * by ORDER_OVERWRITE above.
 */
const getOrderForReleaseStage = (stage?: ReleaseStage): number => {
  switch (stage) {
    case ReleaseStage.beta:
      return 1;
    case ReleaseStage.alpha:
      return 2;
    default:
      return 0;
  }
};
interface ServiceDropdownOption {
  label: string;
  value: string;
  img: JSX.Element;
  releaseStage: ReleaseStage | undefined;
}
const transformConnectorDefinitionToDropdownOption = (item: ConnectorDefinition): ServiceDropdownOption => ({
  label: item.name,
  value: Connector.id(item),
  img: <ConnectorIcon icon={item.icon} />,
  releaseStage: item.releaseStage,
});

const sortUsingOrderOverwrite =
  (orderOverwrite: Record<string, number>) => (a: ServiceDropdownOption, b: ServiceDropdownOption) => {
    const priorityA = orderOverwrite[a.value] ?? 0;
    const priorityB = orderOverwrite[b.value] ?? 0;
    // If they have different priority use the higher priority first, otherwise use the label
    if (priorityA !== priorityB) {
      return priorityB - priorityA;
    } else if (a.releaseStage !== b.releaseStage) {
      return getOrderForReleaseStage(a.releaseStage) - getOrderForReleaseStage(b.releaseStage);
    }
    return naturalComparator(a.label, b.label);
  };

/*
 Returns sorted ServiceDropdownOption[] using overwritten experiment order
 */
export const getSortedDropdownDataUsingExperiment = (
  availableConnectorDefinitions: ConnectorDefinition[],
  orderOverwrite: Record<string, number>
) =>
  availableConnectorDefinitions
    .map(transformConnectorDefinitionToDropdownOption)
    .sort(sortUsingOrderOverwrite(orderOverwrite));
