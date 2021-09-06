import { lazy, Suspense } from "react";
import ReactDOM from "react-dom";
import * as Sentry from "@sentry/react";
import config from "config";

Sentry.init({ dsn: config.sentry.dns });

const CloudApp = lazy(() => import(`packages/cloud/App`));
const App = lazy(() => import(`./App`));

ReactDOM.render(
  <Suspense fallback={null}>
    {process.env.REACT_APP_CLOUD ? <CloudApp /> : <App />}
  </Suspense>,
  document.getElementById("root")
);
