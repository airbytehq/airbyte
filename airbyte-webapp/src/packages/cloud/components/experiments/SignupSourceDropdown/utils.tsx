import { ConnectorIcon } from "components/common/ConnectorIcon";

import { Connector } from "core/domain/connector";
import { ReleaseStage, SourceDefinitionRead } from "core/request/AirbyteClient";
import { naturalComparator } from "utils/objects";

/**
 * Returns the order for a specific release stage label. This will define
 * in what order the different release stages are shown inside the select.
 * They will be shown in an increasing order (i.e. 0 on top)
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
const transformConnectorDefinitionToDropdownOption = (item: SourceDefinitionRead): ServiceDropdownOption => ({
  label: item.name,
  value: Connector.id(item),
  img: <ConnectorIcon icon={item.icon} />,
  releaseStage: item.releaseStage,
});

const sortByReleaseStage = (a: ServiceDropdownOption, b: ServiceDropdownOption) => {
  if (a.releaseStage !== b.releaseStage) {
    return getOrderForReleaseStage(a.releaseStage) - getOrderForReleaseStage(b.releaseStage);
  }
  return naturalComparator(a.label, b.label);
};

export const getSortedDropdownData = (availableConnectorDefinitions: SourceDefinitionRead[]): ServiceDropdownOption[] =>
  availableConnectorDefinitions.map(transformConnectorDefinitionToDropdownOption).sort(sortByReleaseStage);
