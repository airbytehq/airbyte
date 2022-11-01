import React, { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { components, MenuListProps } from "react-select";
import styled from "styled-components";

import { DropDownOptionDataItem } from "components/ui/DropDown";
import { Popout } from "components/ui/Popout";

import { useListCloudWorkspacesAsync } from "packages/cloud/services/workspaces/CloudWorkspacesService";
import { useCurrentWorkspace, useWorkspaceService } from "services/workspaces/WorkspacesService";

import ExitIcon from "./components/ExitIcon";

const BottomElement = styled.div`
  background: ${(props) => props.theme.greyColor0};
  padding: 12px 16px 12px;
  width: 100%;
  min-height: 34px;
  border-top: 1px solid ${(props) => props.theme.greyColor20};
  color: ${(props) => props.theme.primaryColor};
`;

const Block = styled.div`
  cursor: pointer;
  color: ${({ theme }) => theme.primaryColor};
  font-size: 11px;
  line-height: 13px;
  vertical-align: center;

  &:hover {
    opacity: 0.7;
  }
`;

const TextBlock = styled.div`
  margin-left: 10px;
  vertical-align: text-top;
  display: inline-block;
`;

const TopElement = styled.div<{ single: boolean }>`
  font-weight: 500;
  font-size: 14px;
  line-height: 17px;
  display: flex;
  align-items: center;
  padding: 12px 16px 12px;

  & > span {
    display: block;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  ${({ single, theme }) => !single && `border-bottom: 1px solid ${theme.greyColor20};`}
`;

const List = styled.div`
  & .react-select__option {
    & div {
      font-weight: 400;
      font-size: 11px;
      color: #1a194d;
    }
  }
`;

type MenuWithRequestButtonProps = MenuListProps<DropDownOptionDataItem, boolean> & {
  selectedWorkspace: string;
};

const WorkspacesList: React.FC<React.PropsWithChildren<MenuWithRequestButtonProps>> = ({
  children,
  selectedWorkspace,
  ...props
}) => {
  const { exitWorkspace } = useWorkspaceService();

  return (
    <List>
      <TopElement single={props.options.length === 0}>
        <span>{selectedWorkspace}</span>
      </TopElement>
      <components.MenuList {...props}>{children}</components.MenuList>
      <BottomElement>
        <Block onClick={exitWorkspace}>
          <ExitIcon />
          <TextBlock data-testid="workspaces.viewAllWorkspaces">
            <FormattedMessage id="workspaces.viewAllWorkspaces" />
          </TextBlock>
        </Block>
      </BottomElement>
    </List>
  );
};

const WorkspacePopout: React.FC<{
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  children: (props: { onOpen: () => void; value: any }) => React.ReactNode;
}> = ({ children }) => {
  const { formatMessage } = useIntl();
  const { data: workspaceList, isLoading } = useListCloudWorkspacesAsync();
  const { selectWorkspace } = useWorkspaceService();
  const workspace = useCurrentWorkspace();

  const options = useMemo(
    () =>
      workspaceList
        ?.filter((w) => w.workspaceId !== workspace.workspaceId)
        .map((workspace) => ({
          value: workspace.workspaceId,
          label: workspace.name,
        })),
    [workspaceList, workspace]
  );

  return (
    <Popout
      targetComponent={(targetProps) => children({ onOpen: targetProps.onOpen, value: workspace.name })}
      components={{
        MenuList: (props) => <WorkspacesList {...props} selectedWorkspace={workspace.name} />,
      }}
      isSearchable={false}
      options={options}
      isLoading={isLoading}
      loadingMessage={() =>
        formatMessage({
          id: "workspaces.loading",
        })
      }
      value={workspace.slug}
      onChange={({ value }) => selectWorkspace(value)}
    />
  );
};

export { WorkspacePopout };
