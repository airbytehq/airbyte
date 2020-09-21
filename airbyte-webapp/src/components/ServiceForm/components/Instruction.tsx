import { FormattedMessage } from "react-intl";
import React from "react";
import styled from "styled-components";

import { IDataItem } from "../../DropDown/components/ListItem";

type IProps = {
  serviceId: string;
  dropDownData?: Array<IDataItem>;
  url?: string;
};

const LinkToInstruction = styled.a`
  margin-left: 19px;
  font-weight: 500;
  font-size: 14px;
  line-height: 17px;
  text-decoration: underline;

  color: ${({ theme }) => theme.primaryColor};
`;

const Instruction: React.FC<IProps> = ({ dropDownData, serviceId, url }) => {
  const service =
    dropDownData && dropDownData.find(item => item.value === serviceId);

  return service ? (
    <LinkToInstruction
      href={url ? url : "https://docs.airbyte.io/"}
      target="_blank"
    >
      <FormattedMessage
        id="onboarding.instructionsLink"
        values={{ name: service.text }}
      />
    </LinkToInstruction>
  ) : null;
};

export default Instruction;
