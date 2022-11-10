import { useQuery } from "react-query";

import { useConfig } from "config";
import { ConnectorBuilderRequestService } from "core/domain/connectorBuilder/ConnectorBuilderRequestService";
import {
  StreamReadRequestBody,
  StreamReadRequestBodyManifest,
  StreamsListRequestBody,
} from "core/request/ConnectorBuilderClient";
import { useSuspenseQuery } from "services/connector/useSuspenseQuery";
import { useInitService } from "services/useInitService";

const connectorBuilderKeys = {
  all: ["connectorBuilder"] as const,
  read: (streamName: string) => [...connectorBuilderKeys.all, "read", { streamName }] as const,
  list: (manifest: StreamReadRequestBodyManifest) => [...connectorBuilderKeys.all, "list", { manifest }] as const,
  template: ["template"] as const,
};

function useConnectorBuilderService() {
  const config = useConfig();
  return useInitService(
    () => new ConnectorBuilderRequestService(config.connectorBuilderApiUrl),
    [config.connectorBuilderApiUrl]
  );
}

export const useReadStream = (params: StreamReadRequestBody) => {
  const service = useConnectorBuilderService();

  return useQuery(connectorBuilderKeys.read(params.stream), () => service.readStream(params), {
    refetchOnWindowFocus: false,
    enabled: false,
  });
};

export const useListStreams = (params: StreamsListRequestBody) => {
  const service = useConnectorBuilderService();

  return useSuspenseQuery(connectorBuilderKeys.list(params.manifest), () => service.listStreams(params));
};

export const useManifestTemplate = () => {
  const service = useConnectorBuilderService();

  return useSuspenseQuery(connectorBuilderKeys.template, () => service.getManifestTemplate());
};
