import { FormattedMessage } from "react-intl";
import React from "react";
import styled from "styled-components";

import { SourceDefinition } from "core/resources/SourceDefinition";
import { DestinationDefinition } from "core/resources/DestinationDefinition";

type IProps = {
  selectedService: SourceDefinition | DestinationDefinition;
  documentationUrl: string;
};

const LinkToInstruction = styled.a`
  margin-top: 5px;
  font-weight: 500;
  font-size: 14px;
  line-height: 17px;
  text-decoration: underline;
  display: inline-block;

  color: ${({ theme }) => theme.primaryColor};
`;

const Instruction: React.FC<IProps> = ({
  selectedService,
  documentationUrl,
}) => (
  <LinkToInstruction href={documentationUrl} target="_blank">
    <FormattedMessage
      id="onboarding.instructionsLink"
      values={{ name: selectedService.name }}
    />
  </LinkToInstruction>
);

export default Instruction;
