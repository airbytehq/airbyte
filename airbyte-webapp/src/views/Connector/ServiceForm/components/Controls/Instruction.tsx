import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useToggle } from "react-use";

import useDocumentation from "hooks/services/useDocumentation";
import { LoadingPage } from "components";
import { SideView } from "components/SideView";
import { Markdown } from "components/Markdown";
import { DestinationDefinition, SourceDefinition } from "core/domain/connector";

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

const HeaderLink = styled.a`
  color: #fff;
  text-decoration: none;
  display: flex;
  height: 40px;
  align-items: center;
  padding: 0 20px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: rgba(255, 255, 255, 0.2);
  }
`;

const Instruction: React.FC<IProps> = ({
  selectedService,
  documentationUrl,
}) => {
  const [isSideViewOpen, setIsSideViewOpen] = useToggle(false);
  const { data: docs, isLoading } = useDocumentation(documentationUrl);

  return (
    <>
      {isSideViewOpen && (
        <SideView
          onClose={() => setIsSideViewOpen(false)}
          headerLink={
            <HeaderLink
              href={documentationUrl}
              target="_blank"
              rel="noreferrer"
            >
              <FormattedMessage
                id="onboarding.instructionsLink"
                values={{ name: selectedService.name }}
              />
            </HeaderLink>
          }
        >
          {isLoading ? (
            <LoadingPage />
          ) : docs ? (
            <Markdown content={docs} />
          ) : (
            <FormattedMessage id="docs.notFoundError" />
          )}
        </SideView>
      )}
      <LinkToInstruction onClick={() => setIsSideViewOpen(true)}>
        {documentationUrl && <FormattedMessage id="form.setupGuide" />}
      </LinkToInstruction>
    </>
  );
};

export default Instruction;
