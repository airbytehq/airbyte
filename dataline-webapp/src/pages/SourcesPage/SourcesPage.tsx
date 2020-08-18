import React, { Suspense } from "react";
import { Redirect, Route, Switch } from "react-router-dom";

import { Routes } from "../routes";
import LoadingPage from "../../components/LoadingPage";
import AllSourcesPage from "./pages/AllSourcesPage";
import CreateSourcePage from "./pages/CreateSourcePage";

const SourcesPage: React.FC = () => {
  return (
    <Suspense fallback={<LoadingPage />}>
      <Switch>
        <Route path={`${Routes.Source}${Routes.SourceNew}`}>
          <CreateSourcePage />
        </Route>
        <Route path={Routes.Root} exact>
          <AllSourcesPage />
        </Route>
        <Redirect to={Routes.Root} />
      </Switch>
    </Suspense>
  );
};

export default SourcesPage;
