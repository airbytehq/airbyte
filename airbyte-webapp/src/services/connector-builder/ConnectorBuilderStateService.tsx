import { load } from "js-yaml";
import React, { useContext, useState } from "react";
import { useDebounce, useLocalStorage } from "react-use";

import {
  StreamReadRequestBodyConnectorDefinition,
  StreamsListReadStreamsItem,
} from "core/request/ConnectorBuilderClient";

import { useListStreams } from "./ConnectorBuilderApiService";
import { template } from "./YamlTemplate";

interface Context {
  yamlDefinition: string;
  streams: StreamsListReadStreamsItem[];
  selectedStream: StreamsListReadStreamsItem;
  setYamlDefinition: (yamlValue: string) => void;
  setSelectedStream: (streamName: string) => void;
}

export const ConnectorBuilderStateContext = React.createContext<Context | null>(null);

const useYamlDefinition = (): [string, (value: string | undefined) => void] => {
  const [locallyStoredYaml, setLocallyStoredYaml] = useLocalStorage<string>("connectorBuilderYaml", template);
  const [yamlValue, setYamlValue] = useState(locallyStoredYaml ?? "");
  useDebounce(() => setLocallyStoredYaml(yamlValue), 500, [yamlValue]);

  const handleYamlChange = (value: string | undefined) => {
    setYamlValue(value ?? "");
  };

  return [yamlValue, handleYamlChange];
};

const useStreams = () => {
  const [connectorDefinitionYaml] = useYamlDefinition();
  const connectorDefinitionJson = load(connectorDefinitionYaml) as StreamReadRequestBodyConnectorDefinition;
  const streamListRead = useListStreams({ connectorDefinition: connectorDefinitionJson });
  const streams = streamListRead.streams;

  const [selectedStreamName, setSelectedStream] = useState(streamListRead.streams[0].name);
  const selectedStream = streams.find((stream) => stream.name === selectedStreamName) ?? {
    name: selectedStreamName,
    url: "",
  };

  return { streams, selectedStream, setSelectedStream };
};

export const ConnectorBuilderStateProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const [yamlDefinition, setYamlDefinition] = useYamlDefinition();
  const { streams, selectedStream, setSelectedStream } = useStreams();

  const ctx = {
    yamlDefinition,
    streams,
    selectedStream,
    setYamlDefinition,
    setSelectedStream,
  };

  return <ConnectorBuilderStateContext.Provider value={ctx}>{children}</ConnectorBuilderStateContext.Provider>;
};

export const useConnectorBuilderState = (): Context => {
  const connectorBuilderState = useContext(ConnectorBuilderStateContext);
  if (!connectorBuilderState) {
    throw new Error("useConnectorBuilderState must be used within a ConnectorBuilderStateProvider.");
  }

  return connectorBuilderState;
};
