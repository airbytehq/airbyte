import { useField } from "formik";
import React, { useCallback, useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { components } from "react-select";
import { MenuListComponentProps } from "react-select/src/components/Menu";
import styled from "styled-components";

import { ControlLabels, DropDown, DropDownRow } from "components";
import { IDataItem, IProps as OptionProps, OptionView } from "components/base/DropDown/components/Option";
import {
  IProps as SingleValueProps,
  Icon as SingleValueIcon,
  ItemView as SingleValueView,
} from "components/base/DropDown/components/SingleValue";
import { ConnectorIcon } from "components/ConnectorIcon";
import { GAIcon } from "components/icons/GAIcon";

import { Connector, ConnectorDefinition, ReleaseStage } from "core/domain/connector";
import { FormBaseItem } from "core/form/types";
import { useAnalyticsService } from "hooks/services/Analytics";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { naturalComparator } from "utils/objects";

import { WarningMessage } from "../WarningMessage";
import Instruction from "./Instruction";

const BottomElement = styled.div`
  background: ${(props) => props.theme.greyColro0};
  padding: 6px 16px 8px;
  width: 100%;
  min-height: 34px;
  border-top: 1px solid ${(props) => props.theme.greyColor20};
`;

const Block = styled.div`
  cursor: pointer;
  color: ${({ theme }) => theme.textColor};

  &:hover {
    color: ${({ theme }) => theme.primaryColor};
  }
`;

const Text = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const Label = styled.div`
  margin-left: 13px;
  font-weight: 500;
  font-size: 14px;
  line-height: 17px;
`;

const Stage = styled.div`
  padding: 2px 6px;
  height: 14px;
  background: ${({ theme }) => theme.greyColor20};
  border-radius: 25px;
  text-transform: uppercase;
  font-weight: 500;
  font-size: 8px;
  line-height: 10px;
  color: ${({ theme }) => theme.textColor};
`;

const SingleValueContent = styled(components.SingleValue)`
  width: 100%;
  padding-right: 38px;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
`;

type MenuWithRequestButtonProps = MenuListComponentProps<IDataItem, false>;

/**
 * Can be used to overwrite the alphabetical order of connectors in the select.
 * A higher positive number will put the given connector to the top of the list
 * a low negative number to the end of it.
 */
const ORDER_OVERWRITE: Record<string, number> = {};

/**
 * Returns the order for a specific release stage label. This will define
 * in what order the different release stages are shown inside the select.
 * They will be shown in an increasing order (i.e. 0 on top), unless not overwritten
 * by ORDER_OVERWRITE above.
 */
function getOrderForReleaseStage(stage?: ReleaseStage): number {
  switch (stage) {
    case ReleaseStage.BETA:
      return 1;
    case ReleaseStage.ALPHA:
      return 2;
    default:
      return 0;
  }
}

const ConnectorList: React.FC<MenuWithRequestButtonProps> = ({ children, ...props }) => (
  <>
    <components.MenuList {...props}>{children}</components.MenuList>
    <BottomElement>
      <Block onClick={() => props.selectProps.selectProps.onOpenRequestConnectorModal(props.selectProps.inputValue)}>
        <FormattedMessage id="connector.requestConnectorBlock" />
      </Block>
    </BottomElement>
  </>
);

const StageLabel: React.FC<{ releaseStage?: ReleaseStage }> = ({ releaseStage }) => {
  if (!releaseStage) {
    return null;
  }

  if (releaseStage === ReleaseStage.GENERALLY_AVAILABLE) {
    return <GAIcon />;
  }

  return (
    <Stage>
      <FormattedMessage id={`connector.releaseStage.${releaseStage}`} defaultMessage={releaseStage} />
    </Stage>
  );
};

const Option: React.FC<OptionProps> = (props) => {
  return (
    <components.Option {...props}>
      <OptionView data-testid={props.data.label} isSelected={props.isSelected} isDisabled={props.isDisabled}>
        <Text>
          {props.data.img || null}
          <Label>{props.label}</Label>
        </Text>
        <StageLabel releaseStage={props.data.releaseStage} />
      </OptionView>
    </components.Option>
  );
};

const SingleValue: React.FC<SingleValueProps> = (props) => {
  return (
    <SingleValueView>
      {props.data.img && <SingleValueIcon>{props.data.img}</SingleValueIcon>}
      <div>
        <SingleValueContent {...props}>
          {props.data.label}
          <StageLabel releaseStage={props.data.releaseStage} />
        </SingleValueContent>
      </div>
    </SingleValueView>
  );
};

const ConnectorServiceTypeControl: React.FC<{
  property: FormBaseItem;
  formType: "source" | "destination";
  availableServices: ConnectorDefinition[];
  isEditMode?: boolean;
  documentationUrl?: string;
  onChangeServiceType?: (id: string) => void;
  onOpenRequestConnectorModal: (initialName: string) => void;
}> = ({
  property,
  formType,
  isEditMode,
  onChangeServiceType,
  availableServices,
  documentationUrl,
  onOpenRequestConnectorModal,
}) => {
  const { formatMessage } = useIntl();
  const [field, fieldMeta, { setValue }] = useField(property.path);
  const analytics = useAnalyticsService();

  // TODO Begin hack
  // During the Cloud private beta, we let users pick any connector in our catalog.
  // Later on, we realized we shouldn't have allowed using connectors whose platforms required oauth
  // But by that point, some users were already leveraging them, so removing them would crash the app for users
  // instead we'll filter out those connectors from this drop down menu, and retain them in the backend
  // This way, they will not be available for usage in new connections, but they will be available for users
  // already leveraging them.
  // TODO End hack
  const workspace = useCurrentWorkspace();
  const disallowedOauthConnectors =
    // I would prefer to use windowConfigProvider.cloud but that function is async
    window.CLOUD === "true"
      ? [
          "200330b2-ea62-4d11-ac6d-cfe3e3f8ab2b", // Snapchat
          "2470e835-feaf-4db6-96f3-70fd645acc77", // Salesforce Singer
          ...(workspace.workspaceId !== "54135667-ce73-4820-a93c-29fe1510d348" // Shopify workspace for review
            ? ["9da77001-af33-4bcd-be46-6252bf9342b9"] // Shopify
            : []),
        ]
      : [];
  const sortedDropDownData = useMemo(
    () =>
      availableServices
        .filter((item) => !disallowedOauthConnectors.includes(Connector.id(item)))
        .map((item) => ({
          label: item.name,
          value: Connector.id(item),
          img: <ConnectorIcon icon={item.icon} />,
          releaseStage: item.releaseStage,
        }))
        .sort((a, b) => {
          const priorityA = ORDER_OVERWRITE[a.value] ?? 0;
          const priorityB = ORDER_OVERWRITE[b.value] ?? 0;
          // If they have different priority use the higher priority first, otherwise use the label
          if (priorityA !== priorityB) {
            return priorityB - priorityA;
          } else if (a.releaseStage !== b.releaseStage) {
            return getOrderForReleaseStage(a.releaseStage) - getOrderForReleaseStage(b.releaseStage);
          } else {
            return naturalComparator(a.label, b.label);
          }
        }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [availableServices]
  );

  const getNoOptionsMessage = useCallback(
    ({ inputValue }: { inputValue: string }) => {
      analytics.track(
        formType === "source"
          ? "Airbyte.UI.NewSource.NoMatchingConnector"
          : "Airbyte.UI.NewDestination.NoMatchingConnector",
        {
          query: inputValue,
        }
      );
      return formatMessage({ id: "form.noConnectorFound" });
    },
    [analytics, formType, formatMessage]
  );

  const selectedService = React.useMemo(
    () => availableServices.find((s) => Connector.id(s) === field.value),
    [field.value, availableServices]
  );

  const handleSelect = useCallback(
    (item: DropDownRow.IDataItem | null) => {
      if (item) {
        setValue(item.value);
        if (onChangeServiceType) {
          onChangeServiceType(item.value);
        }
      }
    },
    [setValue, onChangeServiceType]
  );

  const onMenuOpen = () => {
    const eventName =
      formType === "source" ? "Airbyte.UI.NewSource.SelectionOpened" : "Airbyte.UI.NewDestination.SelectionOpened";
    analytics.track(eventName, {});
  };

  return (
    <>
      <ControlLabels
        label={formatMessage({
          id: `form.${formType}Type`,
        })}
      >
        <DropDown
          {...field}
          components={{
            MenuList: ConnectorList,
            Option,
            SingleValue,
          }}
          selectProps={{ onOpenRequestConnectorModal }}
          error={!!fieldMeta.error && fieldMeta.touched}
          isDisabled={isEditMode}
          isSearchable
          placeholder={formatMessage({
            id: "form.selectConnector",
          })}
          options={sortedDropDownData}
          onChange={handleSelect}
          onMenuOpen={onMenuOpen}
          noOptionsMessage={getNoOptionsMessage}
        />
      </ControlLabels>
      {selectedService && documentationUrl && (
        <Instruction selectedService={selectedService} documentationUrl={documentationUrl} />
      )}
      {selectedService &&
        (selectedService.releaseStage === ReleaseStage.ALPHA || selectedService.releaseStage === ReleaseStage.BETA) && (
          <WarningMessage stage={selectedService.releaseStage} />
        )}
    </>
  );
};

export { ConnectorServiceTypeControl };
