import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

import { Button } from "components";
import Modal from "components/Modal";

import { JobDebugInfoRead } from "../../../core/request/AirbyteClient";

export interface IProps {
  onClose: () => void;
  jobDebugInfo: JobDebugInfoRead;
}

const Content = styled.div`
  padding: 18px 37px 28px;
  font-size: 14px;
  line-height: 28px;
  max-width: 585px;
`;
const ButtonContent = styled.div`
  padding-top: 27px;
  text-align: right;
`;
const Section = styled.div`
  text-align: right;
  display: flex;
`;
const ButtonWithMargin = styled(Button)`
  margin-right: 9px;
`;

const DebugInfoDetailsModal: React.FC<IProps> = ({ onClose, jobDebugInfo }) => {
  const { formatMessage } = useIntl();

  const getAirbyteVersion = () => {
    return formatMessage(
      {
        id: "ui.keyValuePair",
      },
      {
        key: formatMessage({ id: "sources.airbyteVersion" }),
        value: jobDebugInfo.job.airbyteVersion,
      }
    );
  };

  const getSourceDetails = () => {
    const sourceDetails = formatMessage(
      {
        id: "ui.keyValuePairV2",
      },
      {
        key: jobDebugInfo.job.sourceDefinition.name,
        value: jobDebugInfo.job.sourceDefinition.dockerImageTag,
      }
    );

    return formatMessage(
      {
        id: "ui.keyValuePair",
      },
      {
        key: formatMessage({ id: "connector.source" }),
        value: sourceDetails,
      }
    );
  };

  const getDestinationDetails = () => {
    const destinationDetails = formatMessage(
      {
        id: "ui.keyValuePairV2",
      },
      {
        key: jobDebugInfo.job.destinationDefinition.name,
        value: jobDebugInfo.job.destinationDefinition.dockerImageTag,
      }
    );

    return formatMessage(
      {
        id: "ui.keyValuePair",
      },
      {
        key: formatMessage({ id: "connector.destination" }),
        value: destinationDetails,
      }
    );
  };

  const onCopyClick = () => {
    const airbyteVersionDetails = getAirbyteVersion();
    const sourceDetails = getSourceDetails();
    const destinationDetails = getDestinationDetails();

    navigator.clipboard.writeText([airbyteVersionDetails, sourceDetails, destinationDetails].join("\n"));
  };

  return (
    <Modal
      onClose={onClose}
      title={formatMessage({
        id: "sources.debugInfoModalTitle",
      })}
    >
      <Content>
        <Section>{getAirbyteVersion()}</Section>
        <Section>{getSourceDetails()}</Section>
        <Section>{getDestinationDetails()}</Section>
        <ButtonContent>
          <ButtonWithMargin onClick={onClose} secondary>
            <FormattedMessage id="form.cancel" />
          </ButtonWithMargin>
          <Button onClick={onCopyClick}>
            <FormattedMessage id="sources.copyText" />
          </Button>
        </ButtonContent>
      </Content>
    </Modal>
  );
};

export default DebugInfoDetailsModal;
