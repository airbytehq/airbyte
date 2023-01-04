import { faTrashCan, faCopy } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { FormikErrors, useField } from "formik";
import { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import Indicator from "components/Indicator";
import { CodeEditor } from "components/ui/CodeEditor";
import { Text } from "components/ui/Text";

import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import { BuilderView, useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { BuilderStream } from "../types";
import { AddStreamButton } from "./AddStreamButton";
import { BuilderCard } from "./BuilderCard";
import { BuilderConfigView } from "./BuilderConfigView";
import { BuilderField } from "./BuilderField";
import { BuilderTitle } from "./BuilderTitle";
import { KeyValueListField } from "./KeyValueListField";
import { PaginationSection } from "./PaginationSection";
import styles from "./StreamConfigView.module.scss";
import { StreamSlicerSection } from "./StreamSlicerSection";

interface StreamConfigViewProps {
  streamNum: number;
}

export const StreamConfigView: React.FC<StreamConfigViewProps> = ({ streamNum }) => {
  const streamPath = `streams[${streamNum}]`;
  const streamFieldPath = (fieldPath: string) => `${streamPath}.${fieldPath}`;

  const { formatMessage } = useIntl();
  const [field, meta, helpers] = useField<BuilderStream[]>("streams");
  const currentStreamErrors = meta.error?.[streamNum] as FormikErrors<BuilderStream>;
  const hasSchemaErrors = Boolean(currentStreamErrors?.schema);
  const hasConfigErrors = Boolean(
    Object.keys(currentStreamErrors || {}).filter((errorKey) => errorKey !== "schema").length > 0
  );
  const [selectedTab, setSelectedTab] = useState<"configuration" | "schema">(
    hasSchemaErrors && !hasConfigErrors ? "schema" : "configuration"
  );
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const { setSelectedView, setTestStreamIndex } = useConnectorBuilderState();

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
        setTestStreamIndex(streamToSelect);
        closeConfirmationModal();
      },
    });
  };

  return (
    <BuilderConfigView heading={formatMessage({ id: "connectorBuilder.stream" })}>
      {/* Not using intl for the labels and tooltips in this component in order to keep maintainence simple */}
      <BuilderTitle path={streamFieldPath("name")} label="Stream Name" size="md" />
      <div className={styles.controls}>
        <StreamTab
          label={formatMessage({ id: "connectorBuilder.streamConfiguration" })}
          selected={selectedTab === "configuration"}
          onSelect={() => setSelectedTab("configuration")}
          showErrorIndicator={hasConfigErrors}
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
            setTestStreamIndex(addedStreamNum);
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
      {selectedTab === "configuration" ? (
        <>
          <BuilderCard>
            <BuilderField
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
          <PaginationSection streamFieldPath={streamFieldPath} />
          <StreamSlicerSection streamFieldPath={streamFieldPath} />
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
      {meta.error && (
        <Text className={styles.errorMessage}>
          <FormattedMessage id={meta.error} />
        </Text>
      )}
    </>
  );
};
