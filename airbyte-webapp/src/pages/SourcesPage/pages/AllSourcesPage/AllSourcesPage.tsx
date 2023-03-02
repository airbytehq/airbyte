import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button, MainPageWithScroll } from "components";
import { EmptyResourceListView } from "components/EmptyResourceListView";
import HeadTitle from "components/HeadTitle";
import PageTitle from "components/PageTitle";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useSourceList } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";

import { RoutePaths } from "../../../routePaths";
import SourcesTable from "./components/SourcesTable";

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

const AllSourcesPage: React.FC = () => {
  const { push } = useRouter();
  const { sources } = useSourceList();
  useTrackPage(PageTrackingCodes.SOURCE_LIST);
  const onCreateSource = () => push(`${RoutePaths.SelectSource}`); // SourceNew
  return sources.length ? (
    <MainPageWithScroll
      // withPadding
      headTitle={<HeadTitle titles={[{ id: "admin.sources" }]} />}
      pageTitle={
        <PageTitle
          withPadding
          title=""
          endComponent={
            <Button onClick={onCreateSource} data-id="new-source">
              <BtnInnerContainer>
                <BtnIcon icon={faPlus} />
                <BtnText>
                  <FormattedMessage id="sources.newSource" />
                </BtnText>
              </BtnInnerContainer>
            </Button>
          }
        />
      }
    >
      <SourcesTable sources={sources} />
    </MainPageWithScroll>
  ) : (
    <EmptyResourceListView resourceType="sources" onCreateClick={onCreateSource} />
  );
};

export default AllSourcesPage;
