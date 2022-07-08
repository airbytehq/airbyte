import React, { useCallback, useEffect, useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { components } from "react-select";
import { MenuListComponentProps } from "react-select/src/components/Menu";

import { ControlLabels, DropDown, DropDownRow } from "components";
import { IDataItem, IProps as OptionProps, OptionView } from "components/base/DropDown/components/Option";
import { IProps as SingleValueProps } from "components/base/DropDown/components/SingleValue";
import { ConnectorIcon } from "components/ConnectorIcon";
import { GAIcon } from "components/icons/GAIcon";

import { Connector, ConnectorDefinition } from "core/domain/connector";
import { ReleaseStage } from "core/request/AirbyteClient";
import { useAvailableConnectorDefinitions } from "hooks/domain/connector/useAvailableConnectorDefinitions";
import { useAnalyticsService } from "hooks/services/Analytics";
import { useExperiment } from "hooks/services/Experiment";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { naturalComparator } from "utils/objects";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";

import styles from "./ServiceTypeDropdown.module.scss";

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
    <div className={styles.buttonElement}>
      <div
        className={styles.block}
        onClick={() => props.selectProps.selectProps.onOpenRequestConnectorModal(props.selectProps.inputValue)}
      >
        <FormattedMessage id="connector.requestConnectorBlock" />
      </div>
    </div>
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
    <div className={styles.stage}>
      <FormattedMessage id={`connector.releaseStage.${releaseStage}`} defaultMessage={releaseStage} />
    </div>
  );
};

const Option: React.FC<OptionProps> = (props) => {
  return (
    <components.Option {...props}>
      <OptionView data-testid={props.data.label} isSelected={props.isSelected} isDisabled={props.isDisabled}>
        <div className={styles.text}>
          {props.data.img || null}
          <div className={styles.label}>{props.label}</div>
        </div>
        <StageLabel releaseStage={props.data.releaseStage} />
      </OptionView>
    </components.Option>
  );
};

const SingleValue: React.FC<SingleValueProps> = (props) => {
  return (
    <div className={styles.singleValueView}>
      {props.data.img && <div className={styles.icon}>{props.data.img}</div>}
      <div>
        <div {...props} className={styles.singleValueContent}>
          {props.data.label}
          <StageLabel releaseStage={props.data.releaseStage} />
        </div>
      </div>
    </div>
  );
};

export interface ServiceTypeControlProps {
  formType: "source" | "destination";
  availableServices: ConnectorDefinition[];
  isEditMode?: boolean;
  documentationUrl?: string;
  value?: string | null;
  onChangeServiceType?: (id: string) => void;
  onOpenRequestConnectorModal: (initialName: string) => void;
  disabled?: boolean;
}

const ServiceTypeDropdown: React.FC<ServiceTypeControlProps> = ({
  formType,
  isEditMode,
  onChangeServiceType,
  availableServices,
  documentationUrl,
  onOpenRequestConnectorModal,
  disabled,
  value,
}) => {
  const { formatMessage } = useIntl();
  const orderOverwrite = useExperiment("connector.orderOverwrite", {});
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

  const handleSelect = useCallback(
    (item: DropDownRow.IDataItem | null) => {
      if (item) {
        if (onChangeServiceType) {
          onChangeServiceType(item.value);
        }
      }
    },
    [onChangeServiceType]
  );

  const onMenuOpen = () => {
    const eventName =
      formType === "source" ? "Airbyte.UI.NewSource.SelectionOpened" : "Airbyte.UI.NewDestination.SelectionOpened";
    analytics.track(eventName, {});
  };

  return (
    <ControlLabels
      label={formatMessage({
        id: `form.${formType}Type`,
      })}
    >
      <DropDown
        value={value}
        components={{
          MenuList: ConnectorList,
          Option,
          SingleValue,
        }}
        selectProps={{ onOpenRequestConnectorModal }}
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
  );
};

export { ServiceTypeDropdown };
