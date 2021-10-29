import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useToggle } from "react-use";

import { SourceDefinition } from "core/resources/SourceDefinition";
import { DestinationDefinition } from "core/resources/DestinationDefinition";
import useDocumentation from "hooks/services/useDocumentation";
import { SideView } from "components/SideView";
import { Markdown } from "components/Markdown";

type IProps = {
  selectedService: SourceDefinition | DestinationDefinition;
  documentationUrl: string;
};

const LinkToInstruction = styled.span`
  cursor: pointer;
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
}) => {
  const [isSideViewOpen, setIsSideViewOpen] = useToggle(false);
  const { data: docs } = useDocumentation(documentationUrl);

  return (
    <>
      {isSideViewOpen && (
        <SideView
          onClose={() => setIsSideViewOpen(false)}
          headerLink={
            <a href={documentationUrl} target="_blank" rel="noreferrer">
              <FormattedMessage
                id="onboarding.instructionsLink"
                values={{ name: selectedService.name }}
              />
            </a>
          }
        >
          <Markdown content={docs} />
        </SideView>
      )}
      <LinkToInstruction onClick={() => setIsSideViewOpen(true)}>
        {documentationUrl && <FormattedMessage id="form.setupGuide" />}
      </LinkToInstruction>
    </>
  );
};

export default Instruction;
