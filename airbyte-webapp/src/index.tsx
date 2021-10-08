import { lazy, Suspense } from "react";
import ReactDOM from "react-dom";
import * as Sentry from "@sentry/react";

// We do not follow default config approach that we follow as we want to init
// sentry asap
Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN || window.REACT_APP_SENTRY_DSN,
});

const CloudApp = lazy(() => import(`packages/cloud/App`));
const App = lazy(() => import(`./App`));

ReactDOM.render(
  <Suspense fallback={null}>
    {process.env.REACT_APP_CLOUD || window.CLOUD === "true" ? (
      <CloudApp />
    ) : (
      <App />
    )}
  </Suspense>,
  document.getElementById("root")
);
