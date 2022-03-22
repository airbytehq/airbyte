import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import ContentCard from "components/ContentCard";
import { Button, H5 } from "components";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCopy } from "@fortawesome/free-solid-svg-icons";
import CloneModal from "./components/CloneModal";

type IProps = {
  type: "source" | "destination";
  name: string;
  onClone: (name: string) => void;
};

const TitleBlockComponent = styled(ContentCard)`
  margin-bottom: 12px;
  padding: 19px 20px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Text = styled.div`
  margin-left: 20px;
  font-size: 11px;
  line-height: 13px;
  color: ${({ theme }) => theme.greyColor40};
  white-space: pre-line;
`;

const ButtonText = styled.span`
  margin-right: 15px;
  border-bottom: ${(props) => `1px solid ${props.theme.darkGreyColor}`};
  padding-bottom: 1px;
  font-size: 10px;
`;

const Icon = styled(FontAwesomeIcon)`
  font-size: 14px;
`;

const FlexButton = styled(Button)`
  display: flex;
`;

const TitleBlock: React.FC<IProps> = ({ type, name, onClone }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <TitleBlockComponent>
        <Text>
          <H5 bold>
            <FormattedMessage id={`tables.${type}Settings`} />
          </H5>
        </Text>
        <FlexButton light onClick={() => setIsModalOpen(true)}>
          <ButtonText>
            <FormattedMessage id="sources.cloneText" />
          </ButtonText>
          <Icon icon={faCopy} />
        </FlexButton>
      </TitleBlockComponent>
      {isModalOpen && (
        <CloneModal
          type={type}
          onClose={() => setIsModalOpen(false)}
          name={name}
          onClone={onClone}
        />
      )}
    </>
  );
};

export default TitleBlock;
