import { faTrashCan, faCopy } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { useField } from "formik";
import { useState } from "react";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

import Indicator from "components/Indicator";
import { CodeEditor } from "components/ui/CodeEditor";
import { Text } from "components/ui/Text";

import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import { BuilderView, useConnectorBuilderFormState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { BuilderStream } from "../types";
import { AddStreamButton } from "./AddStreamButton";
import { BuilderCard } from "./BuilderCard";
import { BuilderConfigView } from "./BuilderConfigView";
import { BuilderField } from "./BuilderField";
import { BuilderFieldWithInputs } from "./BuilderFieldWithInputs";
import { BuilderTitle } from "./BuilderTitle";
import { KeyValueListField } from "./KeyValueListField";
import { PaginationSection } from "./PaginationSection";
import styles from "./StreamConfigView.module.scss";
import { StreamSlicerSection } from "./StreamSlicerSection";

interface StreamConfigViewProps {
  streamNum: number;
  hasMultipleStreams: boolean;
}

export const StreamConfigView: React.FC<StreamConfigViewProps> = React.memo(({ streamNum, hasMultipleStreams }) => {
  const { formatMessage } = useIntl();

  const [selectedTab, setSelectedTab] = useState<"configuration" | "schema">("configuration");
  const streamPath = `streams[${streamNum}]`;
  const streamFieldPath = (fieldPath: string) => `${streamPath}.${fieldPath}`;

  return (
    <BuilderConfigView
      heading={formatMessage({ id: "connectorBuilder.stream" })}
      className={hasMultipleStreams ? styles.multiStreams : undefined}
    >
      {/* Not using intl for the labels and tooltips in this component in order to keep maintainence simple */}
      <BuilderTitle path={streamFieldPath("name")} label="Stream Name" size="md" />
      <StreamControls
        streamNum={streamNum}
        selectedTab={selectedTab}
        setSelectedTab={setSelectedTab}
        streamFieldPath={streamFieldPath}
      />
      {selectedTab === "configuration" ? (
        <>
          <BuilderCard>
            <BuilderFieldWithInputs
              type="string"
              path={streamFieldPath("urlPath")}
              label="Path URL"
              tooltip="Path of the endpoint that this stream represents."
            />
            <BuilderField
              type="enum"
              path={streamFieldPath("httpMethod")}
              options={["GET", "POST"]}
              label="HTTP Method"
              tooltip="HTTP method to use for requests sent to the API"
            />
            <BuilderField
              type="array"
              path={streamFieldPath("fieldPointer")}
              label="Record selector"
              tooltip="Pointer into the response that should be extracted as the final record"
            />
            <BuilderField
              type="array"
              path={streamFieldPath("primaryKey")}
              label="Primary key"
              tooltip="Pointer into the response that should be used as the primary key when deduplicating records in the destination"
              optional
            />
          </BuilderCard>
          <PaginationSection streamFieldPath={streamFieldPath} currentStreamIndex={streamNum} />
          <StreamSlicerSection streamFieldPath={streamFieldPath} currentStreamIndex={streamNum} />
          <BuilderCard>
            <KeyValueListField
              path={streamFieldPath("requestOptions.requestParameters")}
              label="Request Parameters"
              tooltip="Parameters to attach to API requests"
            />
            <KeyValueListField
              path={streamFieldPath("requestOptions.requestHeaders")}
              label="Request Headers"
              tooltip="Headers to attach to API requests"
            />
            <KeyValueListField
              path={streamFieldPath("requestOptions.requestBody")}
              label="Request Body"
              tooltip="Body to attach to API requests as url-encoded form values"
            />
          </BuilderCard>
        </>
      ) : (
        <BuilderCard className={styles.schemaEditor}>
          <SchemaEditor streamFieldPath={streamFieldPath} />
        </BuilderCard>
      )}
    </BuilderConfigView>
  );
});

const StreamControls = ({
  streamNum,
  selectedTab,
  setSelectedTab,
  streamFieldPath,
}: {
  streamNum: number;
  streamFieldPath: (path: string) => string;
  setSelectedTab: (tab: "configuration" | "schema") => void;
  selectedTab: "configuration" | "schema";
}) => {
  const { formatMessage } = useIntl();
  const [field, , helpers] = useField<BuilderStream[]>("streams");
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const { setSelectedView } = useConnectorBuilderFormState();
  const [, meta] = useField<string | undefined>(streamFieldPath("schema"));
  const hasSchemaErrors = Boolean(meta.error);

  const handleDelete = () => {
    openConfirmationModal({
      text: "connectorBuilder.deleteStreamModal.text",
      title: "connectorBuilder.deleteStreamModal.title",
      submitButtonText: "connectorBuilder.deleteStreamModal.submitButton",
      onSubmit: () => {
        const updatedStreams = field.value.filter((_, index) => index !== streamNum);
        const streamToSelect = streamNum >= updatedStreams.length ? updatedStreams.length - 1 : streamNum;
        const viewToSelect: BuilderView = updatedStreams.length === 0 ? "global" : streamToSelect;
        helpers.setValue(updatedStreams);
        setSelectedView(viewToSelect);
        closeConfirmationModal();
      },
    });
  };
  return (
    <div className={styles.controls}>
      <StreamTab
        label={formatMessage({ id: "connectorBuilder.streamConfiguration" })}
        selected={selectedTab === "configuration"}
        onSelect={() => setSelectedTab("configuration")}
      />
      <StreamTab
        label={formatMessage({ id: "connectorBuilder.streamSchema" })}
        selected={selectedTab === "schema"}
        onSelect={() => setSelectedTab("schema")}
        showErrorIndicator={hasSchemaErrors}
      />
      <AddStreamButton
        onAddStream={(addedStreamNum) => {
          setSelectedView(addedStreamNum);
        }}
        initialValues={field.value[streamNum]}
        button={
          <button className={styles.controlButton} type="button">
            <FontAwesomeIcon icon={faCopy} />
          </button>
        }
      />
      <button className={classNames(styles.deleteButton, styles.controlButton)} type="button" onClick={handleDelete}>
        <FontAwesomeIcon icon={faTrashCan} />
      </button>
    </div>
  );
};

const StreamTab = ({
  selected,
  label,
  onSelect,
  showErrorIndicator,
}: {
  selected: boolean;
  label: string;
  onSelect: () => void;
  showErrorIndicator?: boolean;
}) => (
  <button type="button" className={classNames(styles.tab, { [styles.selectedTab]: selected })} onClick={onSelect}>
    {label}
    {showErrorIndicator && <Indicator />}
  </button>
);

const SchemaEditor = ({ streamFieldPath }: { streamFieldPath: (fieldPath: string) => string }) => {
  const [field, meta, helpers] = useField<string | undefined>(streamFieldPath("schema"));

  return (
    <>
      <CodeEditor
        value={field.value || ""}
        language="json"
        theme="airbyte-light"
        onChange={(val: string | undefined) => {
          helpers.setValue(val);
        }}
      />
      <Text className={styles.errorMessage}>{meta.error && <FormattedMessage id={meta.error} />}</Text>
    </>
  );
};
