import classNames from "classnames";
import capitalize from "lodash/capitalize";
import { useIntl } from "react-intl";

import { Heading } from "components/ui/Heading";
import { ListBox, ListBoxControlButtonProps } from "components/ui/ListBox";

import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics";
import {
  useConnectorBuilderTestState,
  useConnectorBuilderFormState,
} from "services/connectorBuilder/ConnectorBuilderStateService";

import styles from "./StreamSelector.module.scss";
import { ReactComponent as CaretDownIcon } from "../../ui/ListBox/CaretDownIcon.svg";

interface StreamSelectorProps {
  className?: string;
}

const ControlButton: React.FC<ListBoxControlButtonProps<string>> = ({ selectedOption }) => {
  return (
    <>
      <Heading className={styles.label} as="h1" size="sm">
        {selectedOption.label}
      </Heading>
      <CaretDownIcon className={styles.arrow} />
    </>
  );
};

export const StreamSelector: React.FC<StreamSelectorProps> = ({ className }) => {
  const analyticsService = useAnalyticsService();
  const { formatMessage } = useIntl();
  const { selectedView, setSelectedView } = useConnectorBuilderFormState();
  const { testStreamIndex, setTestStreamIndex } = useConnectorBuilderTestState();

  const streams = useStreamNames();

  const options = streams.map((stream) => {
    const label =
      stream.name && stream.name.trim() ? capitalize(stream.name) : formatMessage({ id: "connectorBuilder.emptyName" });
    return { label, value: stream.name };
  });

  const handleStreamSelect = (selectedStreamName: string) => {
    const selectedStreamIndex = streams.findIndex((stream) => selectedStreamName === stream.name);
    if (selectedStreamIndex >= 0) {
      setTestStreamIndex(selectedStreamIndex);

      if (selectedView !== "global") {
        setSelectedView(selectedStreamIndex);
        analyticsService.track(Namespace.CONNECTOR_BUILDER, Action.STREAM_SELECT, {
          actionDescription: "Stream view selected in testing panel",
          stream_name: selectedStreamName,
        });
      }
    }
  };

  return (
    <ListBox
      className={classNames(className, styles.container)}
      options={options}
      selectedValue={streams[testStreamIndex]?.name ?? formatMessage({ id: "connectorBuilder.noStreamSelected" })}
      onSelect={handleStreamSelect}
      buttonClassName={styles.button}
      controlButton={ControlButton}
    />
  );
};

function useStreamNames() {
  const { builderFormValues, editorView, formValuesValid } = useConnectorBuilderFormState();
  const { streams: testStreams, isFetchingStreamList, streamListErrorMessage } = useConnectorBuilderTestState();

  let streams: Array<{ name: string }> = editorView === "ui" ? builderFormValues.streams : testStreams;

  const testStreamListUpToDate = formValuesValid && !isFetchingStreamList && !streamListErrorMessage;

  if (editorView === "ui" && testStreamListUpToDate) {
    streams = streams.map((stream, index) => ({ name: testStreams[index]?.name || stream.name }));
  }

  return streams;
}
