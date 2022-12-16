import { faTrashCan } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useField } from "formik";
import { useIntl } from "react-intl";

import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import { BuilderView, useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { BuilderStream } from "../types";
import { BuilderCard } from "./BuilderCard";
import { BuilderConfigView } from "./BuilderConfigView";
import { BuilderField } from "./BuilderField";
import { BuilderTitle } from "./BuilderTitle";
import { KeyValueListField } from "./KeyValueListField";
import styles from "./StreamConfigView.module.scss";

interface StreamConfigViewProps {
  streamNum: number;
}

export const StreamConfigView: React.FC<StreamConfigViewProps> = ({ streamNum }) => {
  const { formatMessage } = useIntl();
  const [field, , helpers] = useField<BuilderStream[]>("streams");
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const { setSelectedView, setTestStreamIndex } = useConnectorBuilderState();

  const streamPath = `streams[${streamNum}]`;
  const streamFieldPath = (fieldPath: string) => `${streamPath}.${fieldPath}`;

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
        <button className={styles.deleteButton} type="button" onClick={handleDelete}>
          <FontAwesomeIcon icon={faTrashCan} />
        </button>
      </div>
      <BuilderCard>
        <BuilderField
          type="text"
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
          label="Field Pointer"
          tooltip="Pointer into the response that should be extracted as the final record"
        />
      </BuilderCard>
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
    </BuilderConfigView>
  );
};
