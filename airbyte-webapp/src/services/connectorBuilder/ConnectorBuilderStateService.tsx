import { dump } from "js-yaml";
import React, { useContext, useEffect, useMemo, useState } from "react";
import { useIntl } from "react-intl";
import { useLocalStorage } from "react-use";

import { BuilderFormValues, convertToManifest } from "components/connectorBuilder/types";

import { StreamReadRequestBodyConfig, StreamsListReadStreamsItem } from "core/request/ConnectorBuilderClient";
import { ConnectorManifest } from "core/request/ConnectorManifest";
import { useAppMonitoringService } from "hooks/services/AppMonitoringService";

import { useListStreams } from "./ConnectorBuilderApiService";

export const DEFAULT_BUILDER_FORM_VALUES: BuilderFormValues = {
  global: {
    connectorName: "",
    urlBase: "",
  },
  streams: [],
};

const DEFAULT_JSON_MANIFEST_VALUES: ConnectorManifest = {
  version: "0.1.0",
  check: {
    stream_names: [],
  },
  streams: [],
};

interface Context {
  builderFormValues: BuilderFormValues;
  jsonManifest: ConnectorManifest;
  yamlManifest: string;
  yamlEditorIsMounted: boolean;
  yamlIsValid: boolean;
  streams: StreamsListReadStreamsItem[];
  streamListErrorMessage: string | undefined;
  selectedStream?: StreamsListReadStreamsItem;
  configString: string;
  configJson: StreamReadRequestBodyConfig;
  setBuilderFormValues: (values: BuilderFormValues) => void;
  setJsonManifest: (jsonValue: ConnectorManifest) => void;
  setYamlEditorIsMounted: (value: boolean) => void;
  setYamlIsValid: (value: boolean) => void;
  setSelectedStream: (streamName: string) => void;
  setConfigString: (configString: string) => void;
}

export const ConnectorBuilderStateContext = React.createContext<Context | null>(null);

export const ConnectorBuilderStateProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const { formatMessage } = useIntl();

  // manifest values
  const [builderFormValues, setBuilderFormValues] = useLocalStorage<BuilderFormValues>(
    "connectorBuilderFormValues",
    DEFAULT_BUILDER_FORM_VALUES
  );
  const formValues = builderFormValues ?? DEFAULT_BUILDER_FORM_VALUES;

  const [jsonManifest, setJsonManifest] = useLocalStorage<ConnectorManifest>(
    "connectorBuilderJsonManifest",
    DEFAULT_JSON_MANIFEST_VALUES
  );
  const manifest = jsonManifest ?? DEFAULT_JSON_MANIFEST_VALUES;

  useEffect(() => {
    setJsonManifest(convertToManifest(formValues));
  }, [formValues, setJsonManifest]);

  const [yamlIsValid, setYamlIsValid] = useState(true);
  const [yamlEditorIsMounted, setYamlEditorIsMounted] = useState(true);

  const [yamlManifest, setYamlManifest] = useState("");
  useEffect(() => {
    setYamlManifest(dump(jsonManifest));
  }, [jsonManifest]);

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
    builderFormValues: formValues,
    jsonManifest: manifest,
    yamlManifest,
    yamlEditorIsMounted,
    yamlIsValid,
    streams,
    streamListErrorMessage,
    selectedStream,
    configString,
    configJson,
    setBuilderFormValues,
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
