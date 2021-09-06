import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import Label from "components/Label";
import LabeledToggle from "components/LabeledToggle";
import { useConfig } from "config";
import FeedbackBlock from "../../../components/FeedbackBlock";

export type MetricsFormProps = {
  onChange: (data: { anonymousDataCollection: boolean }) => void;
  anonymousDataCollection?: boolean;
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
  isLoading?: boolean;
};

const FormItem = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  min-height: 33px;
  margin-bottom: 10px;
`;

const DocsLink = styled.a`
  text-decoration: none;
  color: ${({ theme }) => theme.primaryColor};
  cursor: pointer;
`;

const Subtitle = styled(Label)`
  padding-bottom: 9px;
`;

const Text = styled.div`
  font-style: normal;
  font-weight: normal;
  font-size: 13px;
  line-height: 150%;
  padding-bottom: 9px;
`;

const MetricsForm: React.FC<MetricsFormProps> = ({
  onChange,
  anonymousDataCollection,
  successMessage,
  errorMessage,
  isLoading,
}) => {
  const config = useConfig();
  return (
    <>
      <Subtitle>
        <FormattedMessage id="preferences.anonymizeUsage" />
      </Subtitle>
      <Text>
        <FormattedMessage
          id={"preferences.collectData"}
          values={{
            docs: (...docs: React.ReactNode[]) => (
              <DocsLink target="_blank" href={config.ui.docsLink}>
                {docs}
              </DocsLink>
            ),
          }}
        />
      </Text>
      <FormItem>
        <LabeledToggle
          checked={anonymousDataCollection}
          disabled={isLoading}
          label={<FormattedMessage id="preferences.anonymizeData" />}
          onChange={(event) => {
            onChange({ anonymousDataCollection: event.target.checked });
          }}
        />
        <FeedbackBlock
          errorMessage={errorMessage}
          successMessage={successMessage}
          isLoading={isLoading}
        />
      </FormItem>
    </>
  );
};

export default MetricsForm;
