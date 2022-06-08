import React, { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import Label from "components/Label";
import { LabeledSwitch } from "components/LabeledSwitch";

import FeedbackBlock from "../../../components/FeedbackBlock";

export interface NotificationsFormProps {
  onChange: (data: { news: boolean; securityUpdates: boolean }) => void;
  preferencesValues: {
    news: boolean;
    securityUpdates: boolean;
  };
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
  isLoading?: boolean;
}

const FormItem = styled.div`
  margin-bottom: 10px;
`;

const Subtitle = styled(Label)`
  padding-bottom: 9px;
`;

const NotificationsForm: React.FC<NotificationsFormProps> = ({
  onChange,
  preferencesValues,
  successMessage,
  errorMessage,
  isLoading,
}) => {
  const [securityUpdatesUpdating, setSecurityUpdatesUpdating] = useState(false);
  const [newsletterUpdating, setNewsletterUpdating] = useState(false);

  useEffect(() => {
    if (!isLoading) {
      setSecurityUpdatesUpdating(false);
      setNewsletterUpdating(false);
    }
  }, [isLoading]);

  return (
    <>
      <Subtitle>
        <FormattedMessage id="settings.emailNotifications" />
        <FeedbackBlock errorMessage={errorMessage} successMessage={successMessage} isLoading={isLoading} />
      </Subtitle>
      <FormItem>
        <LabeledSwitch
          name="securityUpdates"
          checked={preferencesValues.securityUpdates}
          disabled={isLoading}
          loading={securityUpdatesUpdating}
          label={<FormattedMessage id="settings.securityUpdates" />}
          onChange={(event) => {
            setSecurityUpdatesUpdating(true);
            onChange({
              securityUpdates: event.target.checked,
              news: preferencesValues.news,
            });
          }}
        />
      </FormItem>

      <FormItem>
        <LabeledSwitch
          name="newsletter"
          checked={preferencesValues.news}
          disabled={isLoading}
          loading={newsletterUpdating}
          label={<FormattedMessage id="settings.newsletter" />}
          onChange={(event) => {
            setNewsletterUpdating(true);
            onChange({
              news: event.target.checked,
              securityUpdates: preferencesValues.securityUpdates,
            });
          }}
        />
      </FormItem>
    </>
  );
};

export default NotificationsForm;
