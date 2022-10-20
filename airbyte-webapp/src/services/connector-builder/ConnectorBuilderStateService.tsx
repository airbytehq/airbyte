import { load, YAMLException } from "js-yaml";
import React, { useContext, useEffect, useState } from "react";
import { useDebounce, useLocalStorage } from "react-use";

import {
  StreamsListReadStreamsItem,
  StreamsListRequestBodyConnectorDefinition,
} from "core/request/ConnectorBuilderClient";

import { useListStreams } from "./ConnectorBuilderApiService";
import { template } from "./YamlTemplate";

interface Context {
  yamlDefinition: string;
  jsonDefinition: StreamsListRequestBodyConnectorDefinition;
  streams: StreamsListReadStreamsItem[];
  selectedStream: StreamsListReadStreamsItem;
  setYamlDefinition: (yamlValue: string) => void;
  setSelectedStream: (streamName: string) => void;
}

export const ConnectorBuilderStateContext = React.createContext<Context | null>(null);

const useYamlDefinition = () => {
  const [locallyStoredYaml, setLocallyStoredYaml] = useLocalStorage<string>("connectorBuilderYaml", template);
  const [yamlDefinition, setYamlDefinition] = useState(locallyStoredYaml ?? "");
  useDebounce(() => setLocallyStoredYaml(yamlDefinition), 500, [yamlDefinition]);

  const [jsonDefinition, setJsonDefinition] = useState<StreamsListRequestBodyConnectorDefinition>({});
  useEffect(() => {
    try {
      const json = load(yamlDefinition) as StreamsListRequestBodyConnectorDefinition;
      setJsonDefinition(json);
    } catch (error) {
      if (error instanceof YAMLException) {
        console.log("Connector definition yaml is not valid!");
      }
    }
  }, [yamlDefinition]);

  return { yamlDefinition, jsonDefinition, setYamlDefinition };
};

const useStreams = () => {
  const { jsonDefinition } = useYamlDefinition();
  const streamListRead = useListStreams({ connectorDefinition: jsonDefinition });
  const streams = streamListRead.streams;

  const [selectedStreamName, setSelectedStream] = useState(streamListRead.streams[0].name);
  const selectedStream = streams.find((stream) => stream.name === selectedStreamName) ?? {
    name: selectedStreamName,
    url: "",
  };

  return { streams, selectedStream, setSelectedStream };
};

export const ConnectorBuilderStateProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const { yamlDefinition, jsonDefinition, setYamlDefinition } = useYamlDefinition();
  const { streams, selectedStream, setSelectedStream } = useStreams();

  const ctx = {
    yamlDefinition,
    jsonDefinition,
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
