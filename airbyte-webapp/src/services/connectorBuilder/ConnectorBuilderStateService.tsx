import { dump } from "js-yaml";
import React, { useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { useIntl } from "react-intl";
import { useLocalStorage } from "react-use";

import { BuilderFormValues, convertToManifest } from "components/connectorBuilder/types";

import { PatchedConnectorManifest } from "core/domain/connectorBuilder/PatchedConnectorManifest";
import { StreamReadRequestBodyConfig, StreamsListReadStreamsItem } from "core/request/ConnectorBuilderClient";

import { useListStreams } from "./ConnectorBuilderApiService";

export const DEFAULT_BUILDER_FORM_VALUES: BuilderFormValues = {
  global: {
    connectorName: "",
    urlBase: "",
    authenticator: { type: "NoAuth" },
  },
  inputs: [],
  inferredInputOverrides: {},
  streams: [],
};

const DEFAULT_JSON_MANIFEST_VALUES: PatchedConnectorManifest = {
  version: "0.1.0",
  check: {
    stream_names: [],
  },
  streams: [],
};

export type EditorView = "ui" | "yaml";
export type BuilderView = "global" | "inputs" | number;

interface Context {
  builderFormValues: BuilderFormValues;
  jsonManifest: PatchedConnectorManifest;
  yamlManifest: string;
  yamlEditorIsMounted: boolean;
  yamlIsValid: boolean;
  streams: StreamsListReadStreamsItem[];
  streamListErrorMessage: string | undefined;
  testStreamIndex: number;
  selectedView: BuilderView;
  configJson: StreamReadRequestBodyConfig;
  editorView: EditorView;
  setBuilderFormValues: (values: BuilderFormValues, isInvalid: boolean) => void;
  setJsonManifest: (jsonValue: PatchedConnectorManifest) => void;
  setYamlEditorIsMounted: (value: boolean) => void;
  setYamlIsValid: (value: boolean) => void;
  setTestStreamIndex: (streamIndex: number) => void;
  setSelectedView: (view: BuilderView) => void;
  setConfigJson: (value: StreamReadRequestBodyConfig) => void;
  setEditorView: (editorView: EditorView) => void;
}

export const ConnectorBuilderStateContext = React.createContext<Context | null>(null);

export const ConnectorBuilderStateProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const { formatMessage } = useIntl();

  // manifest values
  const [storedBuilderFormValues, setStoredBuilderFormValues] = useLocalStorage<BuilderFormValues>(
    "connectorBuilderFormValues",
    DEFAULT_BUILDER_FORM_VALUES
  );

  const lastValidBuilderFormValuesRef = useRef<BuilderFormValues>(storedBuilderFormValues as BuilderFormValues);

  const setBuilderFormValues = useCallback(
    (values: BuilderFormValues, isValid: boolean) => {
      setStoredBuilderFormValues(values);
      if (isValid) {
        lastValidBuilderFormValuesRef.current = values;
      }
    },
    [setStoredBuilderFormValues]
  );

  const builderFormValues = useMemo(() => {
    return { ...DEFAULT_BUILDER_FORM_VALUES, ...(storedBuilderFormValues ?? {}) };
  }, [storedBuilderFormValues]);

  const [jsonManifest, setJsonManifest] = useLocalStorage<PatchedConnectorManifest>(
    "connectorBuilderJsonManifest",
    DEFAULT_JSON_MANIFEST_VALUES
  );
  const manifest = jsonManifest ?? DEFAULT_JSON_MANIFEST_VALUES;

  useEffect(() => {
    setJsonManifest(convertToManifest(builderFormValues));
  }, [builderFormValues, setJsonManifest]);

  const [yamlIsValid, setYamlIsValid] = useState(true);
  const [yamlEditorIsMounted, setYamlEditorIsMounted] = useState(true);

  const [yamlManifest, setYamlManifest] = useState("");
  useEffect(() => {
    setYamlManifest(dump(jsonManifest));
  }, [jsonManifest]);

  const [editorView, setEditorView] = useState<EditorView>("ui");

  const lastValidBuilderFormValues = lastValidBuilderFormValuesRef.current;
  /**
   * The json manifest derived from the last valid state of the builder form values.
   * In the yaml view, this is undefined. Can still be invalid in case an invalid state is loaded from localstorage
   */
  const lastValidJsonManifest = useMemo(
    () =>
      editorView !== "ui"
        ? undefined
        : builderFormValues === lastValidBuilderFormValues
        ? jsonManifest
        : convertToManifest(lastValidBuilderFormValues),
    [builderFormValues, editorView, jsonManifest, lastValidBuilderFormValues]
  );

  // config
  const [configJson, setConfigJson] = useState<StreamReadRequestBodyConfig>({});

  // streams
  const {
    data: streamListRead,
    isError: isStreamListError,
    error: streamListError,
  } = useListStreams({ manifest: lastValidJsonManifest || manifest, config: configJson });
  const unknownErrorMessage = formatMessage({ id: "connectorBuilder.unknownError" });
  const streamListErrorMessage = isStreamListError
    ? streamListError instanceof Error
      ? streamListError.message || unknownErrorMessage
      : unknownErrorMessage
    : undefined;
  const streams = useMemo(() => {
    return streamListRead?.streams ?? [];
  }, [streamListRead]);

  const [testStreamIndex, setTestStreamIndex] = useState(0);
  useEffect(() => {
    setTestStreamIndex((prevIndex) =>
      prevIndex >= streams.length && streams.length > 0 ? streams.length - 1 : prevIndex
    );
  }, [streams]);

  const [selectedView, setSelectedView] = useState<BuilderView>("global");

  const ctx = {
    builderFormValues,
    jsonManifest: manifest,
    yamlManifest,
    yamlEditorIsMounted,
    yamlIsValid,
    streams,
    streamListErrorMessage,
    testStreamIndex,
    selectedView,
    configJson,
    editorView,
    setBuilderFormValues,
    setJsonManifest,
    setYamlIsValid,
    setYamlEditorIsMounted,
    setTestStreamIndex,
    setSelectedView,
    setConfigJson,
    setEditorView,
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
  const { streams, testStreamIndex } = useConnectorBuilderState();

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
