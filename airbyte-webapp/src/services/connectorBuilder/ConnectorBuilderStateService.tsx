import React, { useContext, useEffect, useState } from "react";

import {
  StreamReadRequestBodyConfig,
  StreamsListReadStreamsItem,
  StreamsListRequestBodyManifest,
} from "core/request/ConnectorBuilderClient";

import { useListStreams } from "./ConnectorBuilderApiService";

interface Context {
  jsonManifest: StreamsListRequestBodyManifest;
  yamlIsValid: boolean;
  streams: StreamsListReadStreamsItem[];
  selectedStream: StreamsListReadStreamsItem;
  selectedSlice: number;
  selectedPage: number;
  configString: string;
  configJson: StreamReadRequestBodyConfig;
  setJsonManifest: (jsonValue: StreamsListRequestBodyManifest) => void;
  setYamlIsValid: (value: boolean) => void;
  setSelectedStream: (streamName: string) => void;
  setSelectedSlice: (sliceIndex: number) => void;
  setSelectedPage: (pageIndex: number) => void;
  setConfigString: (configString: string) => void;
}

export const ConnectorBuilderStateContext = React.createContext<Context | null>(null);

const useJsonManifest = () => {
  const [jsonManifest, setJsonManifest] = useState<StreamsListRequestBodyManifest>({});
  const [yamlIsValid, setYamlIsValid] = useState(true);

  return { jsonManifest, yamlIsValid, setJsonManifest, setYamlIsValid };
};

const useSelected = () => {
  const { jsonManifest } = useJsonManifest();
  const { configJson } = useConfig();
  const streamListRead = useListStreams({ manifest: jsonManifest, config: configJson });
  const streams = streamListRead.streams;

  const [selectedStreamName, setSelectedStream] = useState(streamListRead.streams[0].name);
  const selectedStream = streams.find((stream) => stream.name === selectedStreamName) ?? {
    name: selectedStreamName,
    url: "",
  };

  const [streamToSelectedSlice, setStreamToSelectedSlice] = useState({ [selectedStreamName]: 0 });
  const setSelectedSlice = (sliceIndex: number) => {
    setStreamToSelectedSlice((prev) => {
      return { ...prev, [selectedStreamName]: sliceIndex };
    });
  };
  const selectedSlice = streamToSelectedSlice[selectedStreamName] ?? 0;

  const [streamToSelectedPage, setStreamToSelectedPage] = useState({ [selectedStreamName]: 0 });
  const setSelectedPage = (pageIndex: number) => {
    setStreamToSelectedPage((prev) => {
      return { ...prev, [selectedStreamName]: pageIndex };
    });
  };
  const selectedPage = streamToSelectedPage[selectedStreamName] ?? 0;

  return { streams, selectedStream, selectedSlice, selectedPage, setSelectedStream, setSelectedSlice, setSelectedPage };
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
  const jsonManifest = useJsonManifest();
  const selected = useSelected();
  const config = useConfig();

  const ctx = {
    ...jsonManifest,
    ...selected,
    ...config,
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
