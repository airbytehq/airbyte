import { faTrashCan } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useFormikContext } from "formik";
import { FormattedMessage } from "react-intl";

import { Heading } from "components/ui/Heading";

import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import { BuilderView, useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { BuilderFormValues } from "../types";
import { BuilderCard } from "./BuilderCard";
import { BuilderField } from "./BuilderField";
import { BuilderTitle } from "./BuilderTitle";
import styles from "./StreamConfigView.module.scss";

interface StreamConfigViewProps {
  streamNum: number;
}

export const StreamConfigView: React.FC<StreamConfigViewProps> = ({ streamNum }) => {
  const { values, setValues } = useFormikContext<BuilderFormValues>();
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
        const streams = values.streams;
        console.log("streams", streams);
        const updatedStreams = [...streams.slice(0, streamNum), ...streams.slice(streamNum + 1)];
        console.log("updatedStreams", updatedStreams);
        const updatedValues = Object.assign(values, { streams: updatedStreams });
        console.log("updatedValues", updatedValues);
        const streamToSelect = streamNum >= updatedStreams.length ? updatedStreams.length - 1 : streamNum;
        console.log("streamToSelect", streamToSelect);
        const viewToSelect: BuilderView = updatedStreams.length === 0 ? "global" : streamToSelect;
        console.log("viewToSelect", viewToSelect);
        setValues(updatedValues);
        setSelectedView(viewToSelect);
        setTestStreamIndex(streamToSelect);
        closeConfirmationModal();
      },
    });
  };

  return (
    <div className={styles.container}>
      <Heading className={styles.heading} as="h1" size="sm">
        <FormattedMessage id="connectorBuilder.stream" />
      </Heading>
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
    </div>
  );
};
