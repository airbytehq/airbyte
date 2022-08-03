import { useField } from "formik";
import React, { useCallback, useEffect, useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { components } from "react-select";
import { MenuListComponentProps } from "react-select/src/components/Menu";
import styled from "styled-components";

import { ControlLabels, DropDown, DropDownRow } from "components";
import { IDataItem, IProps as OptionProps, OptionView } from "components/base/DropDown/components/Option";
import {
  Icon as SingleValueIcon,
  IProps as SingleValueProps,
  ItemView as SingleValueView,
} from "components/base/DropDown/components/SingleValue";
import { ConnectorIcon } from "components/ConnectorIcon";
import { GAIcon } from "components/icons/GAIcon";

import { Action, Namespace } from "core/analytics";
import { Connector, ConnectorDefinition } from "core/domain/connector";
import { FormBaseItem } from "core/form/types";
import { ReleaseStage } from "core/request/AirbyteClient";
import { useAvailableConnectorDefinitions } from "hooks/domain/connector/useAvailableConnectorDefinitions";
import { useAnalyticsService } from "hooks/services/Analytics";
import { useExperiment } from "hooks/services/Experiment";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { naturalComparator } from "utils/objects";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";

import { WarningMessage } from "../WarningMessage";

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
 * Returns the order for a specific release stage label. This will define
 * in what order the different release stages are shown inside the select.
 * They will be shown in an increasing order (i.e. 0 on top), unless not overwritten
 * by ORDER_OVERWRITE above.
 */
function getOrderForReleaseStage(stage?: ReleaseStage): number {
  switch (stage) {
    case ReleaseStage.beta:
      return 1;
    case ReleaseStage.alpha:
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

  if (releaseStage === ReleaseStage.generally_available) {
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

interface ConnectorServiceTypeControlProps {
  property: FormBaseItem;
  formType: "source" | "destination";
  availableServices: ConnectorDefinition[];
  isEditMode?: boolean;
  documentationUrl?: string;
  onChangeServiceType?: (id: string) => void;
  onOpenRequestConnectorModal: (initialName: string) => void;
  disabled?: boolean;
}

const ConnectorServiceTypeControl: React.FC<ConnectorServiceTypeControlProps> = ({
  property,
  formType,
  isEditMode,
  onChangeServiceType,
  availableServices,
  documentationUrl,
  onOpenRequestConnectorModal,
  disabled,
}) => {
  const { formatMessage } = useIntl();
  const orderOverwrite = useExperiment("connector.orderOverwrite", {});
  const [field, fieldMeta, { setValue }] = useField(property.path);
  const analytics = useAnalyticsService();
  const workspace = useCurrentWorkspace();
  const availableConnectorDefinitions = useAvailableConnectorDefinitions(availableServices, workspace);
  const sortedDropDownData = useMemo(
    () =>
      availableConnectorDefinitions
        .map((item) => ({
          label: item.name,
          value: Connector.id(item),
          img: <ConnectorIcon icon={item.icon} />,
          releaseStage: item.releaseStage,
        }))
        .sort((a, b) => {
          const priorityA = orderOverwrite[a.value] ?? 0;
          const priorityB = orderOverwrite[b.value] ?? 0;
          // If they have different priority use the higher priority first, otherwise use the label
          if (priorityA !== priorityB) {
            return priorityB - priorityA;
          } else if (a.releaseStage !== b.releaseStage) {
            return getOrderForReleaseStage(a.releaseStage) - getOrderForReleaseStage(b.releaseStage);
          }
          return naturalComparator(a.label, b.label);
        }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [availableServices, orderOverwrite]
  );

  const { setDocumentationUrl } = useDocumentationPanelContext();

  useEffect(() => setDocumentationUrl(documentationUrl ?? ""), [documentationUrl, setDocumentationUrl]);

  const getNoOptionsMessage = useCallback(
    ({ inputValue }: { inputValue: string }) => {
      analytics.track(formType === "source" ? Namespace.SOURCE : Namespace.DESTINATION, Action.NO_MATCHING_CONNECTOR, {
        actionDescription: "Connector query without results",
        query: inputValue,
      });
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
    analytics.track(formType === "source" ? Namespace.SOURCE : Namespace.DESTINATION, Action.SELECTION_OPENED, {
      actionDescription: "Opened connector type selection",
    });
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
          isDisabled={isEditMode || disabled}
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
      {selectedService &&
        (selectedService.releaseStage === ReleaseStage.alpha || selectedService.releaseStage === ReleaseStage.beta) && (
          <WarningMessage stage={selectedService.releaseStage} />
        )}
    </>
  );
};

export { ConnectorServiceTypeControl };
