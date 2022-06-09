import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useAsyncFn } from "react-use";

import useWorkspace from "hooks/services/useWorkspace";

const useWorkspaceEditor = (): {
  updateData: (data: {
    email?: string;
    anonymousDataCollection: boolean;
    news: boolean;
    securityUpdates: boolean;
  }) => Promise<void>;
  errorMessage: React.ReactNode;
  successMessage: React.ReactNode;
  loading?: boolean;
} => {
  const { updatePreferences } = useWorkspace();
  const [errorMessage, setErrorMessage] = useState<React.ReactNode>(null);
  const [successMessage, setSuccessMessage] = useState<React.ReactNode>(null);

  const [{ loading }, updateData] = useAsyncFn(
    async (data: { news: boolean; securityUpdates: boolean; anonymousDataCollection: boolean; email?: string }) => {
      setErrorMessage(null);
      setSuccessMessage(null);
      try {
        await updatePreferences({
          email: data.email,
          anonymousDataCollection: data.anonymousDataCollection,
          news: data.news,
          securityUpdates: data.securityUpdates,
        });
        setSuccessMessage(<FormattedMessage id="form.changesSaved" />);
      } catch (e) {
        setErrorMessage(<FormattedMessage id="form.someError" />);
      }
    },
    [setErrorMessage, setSuccessMessage]
  );

  return {
    updateData,
    errorMessage,
    successMessage,
    loading,
  };
};

export default useWorkspaceEditor;
