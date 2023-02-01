import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import {
  Button,
  LoadingPage,
  MainPageWithScroll,
  PageTitle,
  // DropDown, DropDownRow
} from "components";
import { EmptyResourceListView } from "components/EmptyResourceListView";
import HeadTitle from "components/HeadTitle";
// import { Pagination } from "components/Pagination";
// import { Separator } from "components/Separator";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useConnectionList } from "hooks/services/useConnectionHook";
import useRouter from "hooks/useRouter";

import { RoutePaths } from "../../../routePaths";
import ConnectionsTable from "./components/ConnectionsTable";

const BtnInnerContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 8px 4px;
`;

const BtnIcon = styled(FontAwesomeIcon)`
  font-size: 16px;
  margin-right: 10px;
`;

const BtnText = styled.div`
  font-weight: 500;
  font-size: 16px;
  color: #ffffff;
`;

// const DDsContainer = styled.div`
//   width: 100%;
//   display: flex;
//   align-items: center;
//   justify-content: flex-end;
//   padding: 0 32px;
// `;

// const DDContainer = styled.div<{
//   margin?: string;
// }>`
//   width: 216px;
//   margin: ${({ margin }) => margin};
// `;

// const Footer = styled.div`
//   width: 100%;
//   display: flex;
//   flex-direction: row;
//   align-items: center;
//   justify-content: center;
// `;

const AllConnectionsPage: React.FC = () => {
  const { push } = useRouter();

  useTrackPage(PageTrackingCodes.CONNECTIONS_LIST);
  const { connections } = useConnectionList();

  const allowCreateConnection = useFeature(FeatureItem.AllowCreateConnection);

  const onCreateClick = () => push(`${RoutePaths.ConnectionNew}`);

  // const StatusOptions: DropDownRow.IDataItem[] = [
  //   { label: "All status", value: "All status" },
  //   { label: "Active", value: "Active" },
  //   { label: "Inactive", value: "Inactive" },
  // ];

  // const SourceOptions: DropDownRow.IDataItem[] = [{ label: "All sources", value: "All sources" }];

  // const DestinationOptions: DropDownRow.IDataItem[] = [{ label: "All destinations", value: "All destinations" }];

  return (
    <Suspense fallback={<LoadingPage />}>
      {connections.length ? (
        <MainPageWithScroll
          withPadding
          headTitle={<HeadTitle titles={[{ title: "Connections" }]} />}
          pageTitle={
            <PageTitle
              title=""
              endComponent={
                <Button onClick={onCreateClick} disabled={!allowCreateConnection} size="m">
                  <BtnInnerContainer>
                    <BtnIcon icon={faPlus} />
                    <BtnText>
                      <FormattedMessage id="connection.newConnection" />
                    </BtnText>
                  </BtnInnerContainer>
                </Button>
              }
            />
          }
        >
          {/* <Separator />
          <DDsContainer>
            <DDContainer margin="0 24px 0 0">
              <DropDown $withBorder $background="white" value={StatusOptions[0].value} options={StatusOptions} />
            </DDContainer>
            <DDContainer margin="0 24px 0 0">
              <DropDown $withBorder $background="white" value={SourceOptions[0].value} options={SourceOptions} />
            </DDContainer>
            <DDContainer>
              <DropDown $withBorder $background="white" value={DestinationOptions[0].value} options={DestinationOptions} />
            </DDContainer>
          </DDsContainer>
          <Separator height="24px" /> */}
          <ConnectionsTable connections={connections} />
          {/* <Separator height="54px" />
          <Footer>
            <Pagination />
          </Footer> */}
        </MainPageWithScroll>
      ) : (
        <EmptyResourceListView
          resourceType="connections"
          onCreateClick={onCreateClick}
          disableCreateButton={!allowCreateConnection}
        />
      )}
    </Suspense>
  );
};

export default AllConnectionsPage;
