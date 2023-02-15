import { useOutletContext } from "react-router-dom";

import { SourceDefinitionRead, SourceRead, WebBackendConnectionListItem } from "core/request/AirbyteClient";
import { useConnectionList } from "hooks/services/useConnectionHook";
import { useGetSource } from "hooks/services/useSourceHook";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";

interface SourceOverviewContext {
  source: SourceRead;
  sourceDefinition: SourceDefinitionRead;
  connections: WebBackendConnectionListItem[];
}

export const useSourceOverviewContext = () => {
  return useOutletContext<SourceOverviewContext>();
};

export const useSetupSourceOverviewContext: (id: string) => SourceOverviewContext = (id: string) => {
  const source = useGetSource(id);
  const sourceDefinition = useSourceDefinition(source.sourceDefinitionId);
  // We load only connections attached to this source to be shown in the connections grid
  const { connections } = useConnectionList({ sourceId: [source.sourceId] });

  return { source, sourceDefinition, connections };
};
