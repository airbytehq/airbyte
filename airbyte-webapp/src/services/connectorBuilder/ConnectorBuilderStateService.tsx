import { load, YAMLException } from "js-yaml";
import React, { useContext, useEffect, useState } from "react";
import { useDebounce, useLocalStorage } from "react-use";

import {
  StreamReadRequestBodyConfig,
  StreamsListReadStreamsItem,
  StreamsListRequestBodyManifest,
} from "core/request/ConnectorBuilderClient";

import { useListStreams } from "./ConnectorBuilderApiService";
import { template } from "./YamlTemplate";

interface Context {
  yamlManifest: string;
  jsonManifest: StreamsListRequestBodyManifest;
  streams: StreamsListReadStreamsItem[];
  selectedStream: StreamsListReadStreamsItem;
  configString: string;
  configJson: StreamReadRequestBodyConfig;
  setYamlManifest: (yamlValue: string) => void;
  setSelectedStream: (streamName: string) => void;
  setConfigString: (configString: string) => void;
}

export const ConnectorBuilderStateContext = React.createContext<Context | null>(null);

const useYamlManifest = () => {
  const [locallyStoredYaml, setLocallyStoredYaml] = useLocalStorage<string>("connectorBuilderYaml", template);
  const [yamlManifest, setYamlManifest] = useState(locallyStoredYaml ?? "");
  useDebounce(() => setLocallyStoredYaml(yamlManifest), 500, [yamlManifest]);

  const [jsonManifest, setJsonManifest] = useState<StreamsListRequestBodyManifest>({});
  useEffect(() => {
    try {
      const json = load(yamlManifest) as StreamsListRequestBodyManifest;
      setJsonManifest(json);
    } catch (err) {
      if (err instanceof YAMLException) {
        console.error(`Connector manifest yaml is not valid! Error: ${err}`);
      }
    }
  }, [yamlManifest]);

  return { yamlManifest, jsonManifest, setYamlManifest };
};

const useStreams = () => {
  const { jsonManifest } = useYamlManifest();
  const streamListRead = useListStreams({ manifest: jsonManifest });
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
      console.error(`Config value is not valid JSON! Error: ${err}`);
    }
  }, [configString]);

  return { configString, configJson, setConfigString };
};

export const ConnectorBuilderStateProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const { yamlManifest, jsonManifest, setYamlManifest } = useYamlManifest();
  const { streams, selectedStream, setSelectedStream } = useStreams();
  const { configString, configJson, setConfigString } = useConfig();

  const ctx = {
    yamlManifest,
    jsonManifest,
    streams,
    selectedStream,
    configString,
    configJson,
    setYamlManifest,
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
