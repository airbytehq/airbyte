import React from "react";
import styled from "styled-components";
import { useIntl, FormattedMessage } from "react-intl";

import Modal from "components/Modal";
import { Button } from "components";

import { JobDebugInfoMeta } from "core/domain/job";

export type IProps = {
  onClose: () => void;
  jobDebugInfo: JobDebugInfoMeta;
};

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
const Label = styled.div`
  padding-right: 20px;
  font-weight: bold;
`;
const ButtonWithMargin = styled(Button)`
  margin-right: 9px;
`;

const DebugInfoDetailsModal: React.FC<IProps> = ({ onClose, jobDebugInfo }) => {
  const formatMessage = useIntl().formatMessage;

  const getAirbyteVersion = () => {
    return jobDebugInfo.airbyteVersion;
  };

  const getSourceDetails = () => {
    return `${jobDebugInfo.sourceDefinition.name}(${jobDebugInfo.sourceDefinition.dockerImageTag})`;
  };

  const getDestinationDetails = () => {
    return `${jobDebugInfo.destinationDefinition.name}(${jobDebugInfo.destinationDefinition.dockerImageTag})`;
  };

  const onCopyClick = () => {
    navigator.clipboard.writeText(`${formatMessage({
      id: "sources.airbyteVersion",
    })}: ${getAirbyteVersion()} \n${formatMessage({
      id: "connector.source",
    })}: ${getSourceDetails()} \n${formatMessage({
      id: "connector.destination",
    })}: ${getDestinationDetails()}
    `);
  };

  return (
    <Modal
      onClose={onClose}
      title={formatMessage({
        id: "sources.debugInfoModalTitle",
      })}
    >
      <Content>
        <Section>
          <Label>
            <FormattedMessage id="sources.airbyteVersion" />:
          </Label>
          <div>{getAirbyteVersion()}</div>
        </Section>
        <Section>
          <Label>
            <FormattedMessage id="connector.source" />:
          </Label>
          <div>{getSourceDetails()}</div>
        </Section>
        <Section>
          <Label>
            <FormattedMessage id="connector.destination" />:
          </Label>
          <div>{getDestinationDetails()}</div>
        </Section>
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
