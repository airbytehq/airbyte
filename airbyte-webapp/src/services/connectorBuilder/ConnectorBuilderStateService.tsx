import { dump } from "js-yaml";
import React, { useContext, useEffect, useMemo, useState } from "react";
import { useIntl } from "react-intl";
import { useLocalStorage } from "react-use";

import { BuilderFormValues, convertToManifest } from "components/connectorBuilder/types";

import { StreamReadRequestBodyConfig, StreamsListReadStreamsItem } from "core/request/ConnectorBuilderClient";
import { ConnectorManifest } from "core/request/ConnectorManifest";

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

type EditorView = "ui" | "yaml";
export type BuilderView = "global" | number;

interface StateContext {
  builderFormValues: BuilderFormValues;
  jsonManifest: ConnectorManifest;
  yamlManifest: string;
  yamlEditorIsMounted: boolean;
  yamlIsValid: boolean;
  testStreamIndex: number;
  selectedView: BuilderView;
  configString: string;
  configJson: StreamReadRequestBodyConfig;
  editorView: EditorView;
  setBuilderFormValues: (values: BuilderFormValues) => void;
  setJsonManifest: (jsonValue: ConnectorManifest) => void;
  setYamlEditorIsMounted: (value: boolean) => void;
  setYamlIsValid: (value: boolean) => void;
  setTestStreamIndex: (streamIndex: number) => void;
  setSelectedView: (view: BuilderView) => void;
  setConfigString: (configString: string) => void;
  setEditorView: (editorView: EditorView) => void;
}

interface APIContext {
  streams: StreamsListReadStreamsItem[];
  streamListErrorMessage: string | undefined;
}

export const ConnectorBuilderStateContext = React.createContext<StateContext | null>(null);
export const ConnectorBuilderAPIContext = React.createContext<APIContext | null>(null);

export const ConnectorBuilderStateProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
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

  const [editorView, setEditorView] = useState<EditorView>("ui");

  const derivedJsonManifest = useMemo(
    () => (editorView === "yaml" ? manifest : convertToManifest(formValues)),
    [editorView, formValues, manifest]
  );

  const [yamlIsValid, setYamlIsValid] = useState(true);
  const [yamlEditorIsMounted, setYamlEditorIsMounted] = useState(true);

  const yamlManifest = useMemo(() => dump(derivedJsonManifest), [derivedJsonManifest]);

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

  const [testStreamIndex, setTestStreamIndex] = useState(0);

  const [selectedView, setSelectedView] = useState<BuilderView>("global");

  const ctx = {
    builderFormValues: formValues,
    jsonManifest: derivedJsonManifest,
    yamlManifest,
    yamlEditorIsMounted,
    yamlIsValid,
    testStreamIndex,
    selectedView,
    configString,
    configJson,
    editorView,
    setBuilderFormValues,
    setJsonManifest,
    setYamlIsValid,
    setYamlEditorIsMounted,
    setTestStreamIndex,
    setSelectedView,
    setConfigString,
    setEditorView,
  };

  return <ConnectorBuilderStateContext.Provider value={ctx}>{children}</ConnectorBuilderStateContext.Provider>;
};

export const ConnectorBuilderAPIProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const { formatMessage } = useIntl();
  const { jsonManifest, configJson, testStreamIndex, setTestStreamIndex } = useConnectorBuilderState();

  const manifest = jsonManifest ?? DEFAULT_JSON_MANIFEST_VALUES;

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

  useEffect(() => {
    if (testStreamIndex >= streams.length && streams.length > 0) {
      setTestStreamIndex(streams.length - 1);
    }
  }, [streams, testStreamIndex, setTestStreamIndex]);

  const ctx = {
    streams,
    streamListErrorMessage,
  };

  return <ConnectorBuilderAPIContext.Provider value={ctx}>{children}</ConnectorBuilderAPIContext.Provider>;
};

export const useConnectorBuilderAPI = (): APIContext => {
  const connectorBuilderState = useContext(ConnectorBuilderAPIContext);
  if (!connectorBuilderState) {
    throw new Error("useConnectorBuilderAPI must be used within a ConnectorBuilderAPIProvider.");
  }

  return connectorBuilderState;
};

export const useConnectorBuilderState = (): StateContext => {
  const connectorBuilderState = useContext(ConnectorBuilderStateContext);
  if (!connectorBuilderState) {
    throw new Error("useConnectorBuilderState must be used within a ConnectorBuilderStateProvider.");
  }

  return connectorBuilderState;
};

export const useSelectedPageAndSlice = () => {
  const { testStreamIndex } = useConnectorBuilderState();
  const { streams } = useConnectorBuilderAPI();

  const selectedStreamName = streams[testStreamIndex].name;

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
