import React, { useContext, useEffect, useMemo, useState } from "react";
import { useIntl } from "react-intl";
import { useLocalStorage } from "react-use";

import { StreamReadRequestBodyConfig, StreamsListReadStreamsItem } from "core/request/ConnectorBuilderClient";
import { ConnectorManifest } from "core/request/ConnectorManifest";
import { useAppMonitoringService } from "hooks/services/AppMonitoringService";

import { useListStreams } from "./ConnectorBuilderApiService";

interface Context {
  jsonManifest: ConnectorManifest;
  yamlEditorIsMounted: boolean;
  yamlIsValid: boolean;
  streams: StreamsListReadStreamsItem[];
  streamListErrorMessage: string | undefined;
  selectedStream?: StreamsListReadStreamsItem;
  configString: string;
  configJson: StreamReadRequestBodyConfig;
  setJsonManifest: (jsonValue: ConnectorManifest) => void;
  setYamlEditorIsMounted: (value: boolean) => void;
  setYamlIsValid: (value: boolean) => void;
  setSelectedStream: (streamName: string) => void;
  setConfigString: (configString: string) => void;
}

export const ConnectorBuilderStateContext = React.createContext<Context | null>(null);

export const ConnectorBuilderStateProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const { formatMessage } = useIntl();

  // json manifest
  const defaultJsonManifest = {
    version: "1.0.0",
    check: {
      stream_names: [],
    },
    streams: [],
  };
  const [jsonManifest, setJsonManifest] = useLocalStorage<ConnectorManifest>(
    "connectorBuilderManifest",
    defaultJsonManifest
  );
  const manifest = jsonManifest ?? defaultJsonManifest;
  const [yamlIsValid, setYamlIsValid] = useState(true);
  const [yamlEditorIsMounted, setYamlEditorIsMounted] = useState(true);

  // config
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

  console.log("manifest", manifest);

  // streams
  const {
    data: streamListRead,
    isError: isStreamListError,
    error: streamListError,
  } = useListStreams({ manifest, config: configJson });
  const unknownErrorMessage = formatMessage({ id: "connectorBuilder.unknownError" });
  const streamListErrorMessage = isStreamListError
    ? streamListError instanceof Error
      ? streamListError.message || unknownErrorMessage
      : unknownErrorMessage
    : undefined;
  const streams = useMemo(() => {
    return streamListRead?.streams ?? [];
  }, [streamListRead]);
  // const streamListErrorMessage = undefined;
  // const streams = useMemo(() => [{ name: "stream1", url: "url1" }], []);
  const firstStreamName = streams.length > 0 ? streams[0].name : undefined;

  const [selectedStreamName, setSelectedStream] = useState(firstStreamName);
  useEffect(() => {
    setSelectedStream((prevSelected) =>
      prevSelected !== undefined && streams.map((stream) => stream.name).includes(prevSelected)
        ? prevSelected
        : firstStreamName
    );
  }, [streams, firstStreamName]);

  const selectedStream = streams.find((stream) => stream.name === selectedStreamName);

  const ctx = {
    jsonManifest: manifest,
    yamlEditorIsMounted,
    yamlIsValid,
    streams,
    streamListErrorMessage,
    selectedStream,
    configString,
    configJson,
    setJsonManifest,
    setYamlIsValid,
    setYamlEditorIsMounted,
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

export const useSelectedPageAndSlice = () => {
  const { trackError } = useAppMonitoringService();
  const { selectedStream } = useConnectorBuilderState();

  // this case should never be reached, as this hook should only be called in components that are only rendered when a stream is selected
  if (selectedStream === undefined) {
    const err = new Error("useSelectedPageAndSlice called when no stream is selected");
    trackError(err, { id: "useSelectedPageAndSlice.noSelectedStream" });
    throw err;
  }

  const selectedStreamName = selectedStream.name;

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

  return { selectedSlice, selectedPage, setSelectedSlice, setSelectedPage };
};
