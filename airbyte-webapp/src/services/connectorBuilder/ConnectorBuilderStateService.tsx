import { dump } from "js-yaml";
import React, { useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { useIntl } from "react-intl";
import { UseQueryResult } from "react-query";

import {
  BuilderFormValues,
  convertToManifest,
  DEFAULT_BUILDER_FORM_VALUES,
  DEFAULT_JSON_MANIFEST_VALUES,
  EditorView,
} from "components/connectorBuilder/types";

import {
  StreamRead,
  StreamReadRequestBodyConfig,
  StreamsListReadStreamsItem,
} from "core/request/ConnectorBuilderClient";
import { ConnectorManifest, DeclarativeComponentSchema } from "core/request/ConnectorManifest";

import { useListStreams, useReadStream } from "./ConnectorBuilderApiService";
import { useConnectorBuilderLocalStorage } from "./ConnectorBuilderLocalStorageService";

export type BuilderView = "global" | "inputs" | number;

interface FormStateContext {
  builderFormValues: BuilderFormValues;
  formValuesValid: boolean;
  jsonManifest: ConnectorManifest;
  lastValidJsonManifest: DeclarativeComponentSchema | undefined;
  yamlManifest: string;
  yamlEditorIsMounted: boolean;
  yamlIsValid: boolean;
  selectedView: BuilderView;
  editorView: EditorView;
  setBuilderFormValues: (values: BuilderFormValues, isInvalid: boolean) => void;
  setJsonManifest: (jsonValue: ConnectorManifest) => void;
  setYamlEditorIsMounted: (value: boolean) => void;
  setYamlIsValid: (value: boolean) => void;
  setSelectedView: (view: BuilderView) => void;
  setEditorView: (editorView: EditorView) => void;
}

interface TestStateContext {
  streams: StreamsListReadStreamsItem[];
  streamListErrorMessage: string | undefined;
  testInputJson: StreamReadRequestBodyConfig;
  setTestInputJson: (value: StreamReadRequestBodyConfig) => void;
  setTestStreamIndex: (streamIndex: number) => void;
  testStreamIndex: number;
  streamRead: UseQueryResult<StreamRead, unknown>;
  isFetchingStreamList: boolean;
}

export const ConnectorBuilderFormStateContext = React.createContext<FormStateContext | null>(null);
export const ConnectorBuilderTestStateContext = React.createContext<TestStateContext | null>(null);

export const ConnectorBuilderFormStateProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const {
    storedFormValues,
    setStoredFormValues,
    storedManifest,
    setStoredManifest,
    storedEditorView,
    setStoredEditorView,
  } = useConnectorBuilderLocalStorage();

  const lastValidBuilderFormValuesRef = useRef<BuilderFormValues>(storedFormValues);
  const currentBuilderFormValuesRef = useRef<BuilderFormValues>(storedFormValues);

  const [formValuesValid, setFormValuesValid] = useState(true);

  const setBuilderFormValues = useCallback(
    (values: BuilderFormValues, isValid: boolean) => {
      if (isValid) {
        // update ref first because calling setStoredBuilderFormValues might synchronously kick off a react render cycle.
        lastValidBuilderFormValuesRef.current = values;
      }
      currentBuilderFormValuesRef.current = values;
      setStoredFormValues(values);
      setFormValuesValid(isValid);
    },
    [setStoredFormValues]
  );

  // use the ref for the current builder form values because useLocalStorage will always serialize and deserialize the whole object,
  // changing all the references which re-triggers all memoizations
  const builderFormValues = currentBuilderFormValuesRef.current || DEFAULT_BUILDER_FORM_VALUES;

  const derivedJsonManifest = useMemo(
    () => (storedEditorView === "yaml" ? storedManifest : convertToManifest(builderFormValues)),
    [storedEditorView, builderFormValues, storedManifest]
  );

  const manifestRef = useRef(derivedJsonManifest);
  manifestRef.current = derivedJsonManifest;

  const setEditorView = useCallback(
    (view: EditorView) => {
      if (view === "yaml") {
        // when switching to yaml, store the currently derived json manifest
        setStoredManifest(manifestRef.current);
      }
      setStoredEditorView(view);
    },
    [setStoredEditorView, setStoredManifest]
  );

  const [yamlIsValid, setYamlIsValid] = useState(true);
  const [yamlEditorIsMounted, setYamlEditorIsMounted] = useState(true);

  const yamlManifest = useMemo(
    () =>
      dump(derivedJsonManifest, {
        noRefs: true,
      }),
    [derivedJsonManifest]
  );

  const lastValidBuilderFormValues = lastValidBuilderFormValuesRef.current;
  /**
   * The json manifest derived from the last valid state of the builder form values.
   * In the yaml view, this is undefined. Can still be invalid in case an invalid state is loaded from localstorage
   */
  const lastValidJsonManifest = useMemo(
    () =>
      storedEditorView !== "ui"
        ? storedManifest
        : builderFormValues === lastValidBuilderFormValues
        ? derivedJsonManifest
        : convertToManifest(lastValidBuilderFormValues),
    [builderFormValues, storedEditorView, storedManifest, derivedJsonManifest, lastValidBuilderFormValues]
  );

  const [selectedView, setSelectedView] = useState<BuilderView>("global");

  const ctx = {
    builderFormValues,
    formValuesValid,
    jsonManifest: derivedJsonManifest,
    lastValidJsonManifest,
    yamlManifest,
    yamlEditorIsMounted,
    yamlIsValid,
    selectedView,
    editorView: storedEditorView,
    setBuilderFormValues,
    setJsonManifest: setStoredManifest,
    setYamlIsValid,
    setYamlEditorIsMounted,
    setSelectedView,
    setEditorView,
  };

  return <ConnectorBuilderFormStateContext.Provider value={ctx}>{children}</ConnectorBuilderFormStateContext.Provider>;
};

export const ConnectorBuilderTestStateProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const { formatMessage } = useIntl();
  const { lastValidJsonManifest, selectedView } = useConnectorBuilderFormState();

  const manifest = lastValidJsonManifest ?? DEFAULT_JSON_MANIFEST_VALUES;

  // config
  const [testInputJson, setTestInputJson] = useState<StreamReadRequestBodyConfig>({});

  // streams
  const {
    data: streamListRead,
    isError: isStreamListError,
    error: streamListError,
    isFetching: isFetchingStreamList,
  } = useListStreams({ manifest, config: testInputJson });
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
    if (typeof selectedView === "number") {
      setTestStreamIndex(selectedView);
    }
  }, [selectedView]);

  const streamRead = useReadStream({
    manifest,
    stream: streams[testStreamIndex]?.name,
    config: testInputJson,
  });

  const ctx = {
    streams,
    streamListErrorMessage,
    testInputJson,
    setTestInputJson,
    testStreamIndex,
    setTestStreamIndex,
    streamRead,
    isFetchingStreamList,
  };

  return <ConnectorBuilderTestStateContext.Provider value={ctx}>{children}</ConnectorBuilderTestStateContext.Provider>;
};

export const useConnectorBuilderTestState = (): TestStateContext => {
  const connectorBuilderState = useContext(ConnectorBuilderTestStateContext);
  if (!connectorBuilderState) {
    throw new Error("useConnectorBuilderTestStae must be used within a ConnectorBuilderTestStateProvider.");
  }

  return connectorBuilderState;
};

export const useConnectorBuilderFormState = (): FormStateContext => {
  const connectorBuilderState = useContext(ConnectorBuilderFormStateContext);
  if (!connectorBuilderState) {
    throw new Error("useConnectorBuilderFormState must be used within a ConnectorBuilderFormStateProvider.");
  }

  return connectorBuilderState;
};

export const useSelectedPageAndSlice = () => {
  const { streams, testStreamIndex } = useConnectorBuilderTestState();

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
