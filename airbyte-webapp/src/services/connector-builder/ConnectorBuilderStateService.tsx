import { load, YAMLException } from "js-yaml";
import React, { useContext, useEffect, useState } from "react";
import { useDebounce, useLocalStorage } from "react-use";

import {
  StreamReadRequestBodyConfig,
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
  configString: string;
  configJson: StreamReadRequestBodyConfig;
  setYamlDefinition: (yamlValue: string) => void;
  setSelectedStream: (streamName: string) => void;
  setConfigString: (configString: string) => void;
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
    } catch (err) {
      if (err instanceof YAMLException) {
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

const useConfig = () => {
  const [configString, setConfigString] = useState("{\n  \n}");
  const [configJson, setConfigJson] = useState<StreamReadRequestBodyConfig>({});

  useEffect(() => {
    try {
      const json = JSON.parse(configString) as StreamReadRequestBodyConfig;
      setConfigJson(json);
    } catch (err) {
      console.log("Config value is not valid JSON!");
    }
  }, [configString]);

  return { configString, configJson, setConfigString };
};

export const ConnectorBuilderStateProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const { yamlDefinition, jsonDefinition, setYamlDefinition } = useYamlDefinition();
  const { streams, selectedStream, setSelectedStream } = useStreams();
  const { configString, configJson, setConfigString } = useConfig();

  const ctx = {
    yamlDefinition,
    jsonDefinition,
    streams,
    selectedStream,
    configString,
    configJson,
    setYamlDefinition,
    setSelectedStream,
    setConfigString,
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
