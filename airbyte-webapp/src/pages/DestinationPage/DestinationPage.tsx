// TODO: replace to separate page
// import React, { useState } from "react";
// import { FormattedMessage } from "react-intl";
// import styled from "styled-components";
// import { useResource } from "rest-hooks";
//
// import PageTitle from "../../components/PageTitle";
// import ContentCard from "../../components/ContentCard";
// import ServiceForm from "../../components/ServiceForm";
// import DestinationResource from "../../core/resources/Destination";
// import config from "../../config";
// import DestinationDefinitionSpecificationResource from "../../core/resources/DestinationDefinitionSpecification";
// import DestinationDefinitionResource from "../../core/resources/DestinationDefinition";
// import useDestination from "../../components/hooks/services/useDestinationHook";
//
// const Content = styled.div`
//   width: 100%;
//   max-width: 638px;
//   margin: 19px auto;
// `;
//
// const DestinationPage: React.FC = () => {
//   const [saved, setSaved] = useState(false);
//   const [errorMessage, setErrorMessage] = useState("");
//
//   const { destinations } = useResource(DestinationResource.listShape(), {
//     workspaceId: config.ui.workspaceId
//   });
//   const currentDestination: DestinationResource = destinations[0]; // Now we have only one destination. If we support multiple destinations we will fix this line
//   const destinationSpecification = useResource(
//     DestinationDefinitionSpecificationResource.detailShape(),
//     {
//       destinationDefinitionId: currentDestination.destinationDefinitionId
//     }
//   );
//   const destination = useResource(DestinationDefinitionResource.detailShape(), {
//     destinationDefinitionId: currentDestination.destinationDefinitionId
//   });
//   const { updateDestination } = useDestination();
//
//   const onSubmitForm = async (values: {
//     name: string;
//     serviceType: string;
//     connectionConfiguration?: any;
//   }) => {
//     setErrorMessage("");
//     const result = await updateDestination({
//       values,
//       destinationId: currentDestination.destinationId
//     });
//
//     if (result.status === "failure") {
//       setErrorMessage(result.message);
//     } else {
//       setSaved(true);
//     }
//   };
//
//   return (
//     <>
//       <PageTitle
//         title={<FormattedMessage id="sidebar.destination" />}
//         withLine
//       />
//       <Content>
//         <ContentCard
//           title={<FormattedMessage id="destination.destinationSettings" />}
//         >
//           <ServiceForm
//             isEditMode
//             onSubmit={onSubmitForm}
//             formType="destination"
//             dropDownData={[
//               {
//                 value: destination.destinationDefinitionId,
//                 text: destination.name,
//                 img: "/default-logo-catalog.svg"
//               }
//             ]}
//             formValues={{
//               ...currentDestination,
//               serviceType: destination.destinationDefinitionId
//             }}
//             specifications={destinationSpecification.connectionSpecification}
//             successMessage={
//               saved && <FormattedMessage id="form.changesSaved" />
//             }
//             errorMessage={errorMessage}
//           />
//         </ContentCard>
//       </Content>
//     </>
//   );
// };
//
// export default DestinationPage;

import React, { Suspense } from "react";
import { Redirect, Route, Switch } from "react-router-dom";
import { NetworkErrorBoundary as ErrorBoundary } from "rest-hooks";

import { Routes } from "../routes";
import LoadingPage from "../../components/LoadingPage";
import AllDestinationsPage from "./pages/AllDestinationsPage";
import DestinationItemPage from "./pages/DestinationItemPage";
import ConnectionPage from "../ConnectionPage";

const FallbackRootRedirector = () => <Redirect to={Routes.Destination} />;

const DestinationsPage: React.FC = () => {
  return (
    <Suspense fallback={<LoadingPage />}>
      <Switch>
        <Route path={Routes.Destination} exact>
          <AllDestinationsPage />
        </Route>
        <Route path={`${Routes.Destination}${Routes.Connection}/:id`}>
          <ErrorBoundary fallbackComponent={FallbackRootRedirector}>
            <ConnectionPage />
          </ErrorBoundary>
        </Route>
        <Route path={`${Routes.Destination}/:id`}>
          <ErrorBoundary fallbackComponent={FallbackRootRedirector}>
            <DestinationItemPage />
          </ErrorBoundary>
        </Route>
        <Redirect to={Routes.Root} />
      </Switch>
    </Suspense>
  );
};

export default DestinationsPage;
