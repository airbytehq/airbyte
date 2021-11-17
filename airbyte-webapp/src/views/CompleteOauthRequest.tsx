import React from "react";
import { LoadingPage } from "components";
import { useResolveRedirect } from "hooks/services/useConnectorAuth";

const CompleteOauthRequest: React.FC = React.memo(() => {
  useResolveRedirect();

  return <LoadingPage />;
});

export { CompleteOauthRequest };
