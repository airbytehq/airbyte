import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useCallback, useEffect, useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { components } from "react-select";
import { MenuListProps } from "react-select";

import { GAIcon } from "components/icons/GAIcon";
import { ControlLabels } from "components/LabeledControl";
import {
  DropDown,
  DropDownOptionDataItem,
  DropDownOptionProps,
  OptionView,
  SingleValueIcon,
  SingleValueProps,
  SingleValueView,
} from "components/ui/DropDown";
import { Text } from "components/ui/Text";

import { Connector, ConnectorDefinition } from "core/domain/connector";
import { ReleaseStage } from "core/request/AirbyteClient";
import { useAvailableConnectorDefinitions } from "hooks/domain/connector/useAvailableConnectorDefinitions";
import { useExperiment } from "hooks/services/Experiment";
import { useModalService } from "hooks/services/Modal";
import { useCurrentWorkspace } from "hooks/services/useWorkspace";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";
import RequestConnectorModal from "views/Connector/RequestConnectorModal";

import { WarningMessage } from "../../WarningMessage";
import styles from "./ConnectorServiceTypeControl.module.scss";
import { useAnalyticsTrackFunctions } from "./useAnalyticsTrackFunctions";
import { getSortedDropdownDataUsingExperiment } from "./utils";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type MenuWithRequestButtonProps = MenuListProps<DropDownOptionDataItem, false> & { selectProps: any };

const ConnectorList: React.FC<React.PropsWithChildren<MenuWithRequestButtonProps>> = ({ children, ...props }) => (
  <>
    <components.MenuList {...props}>{children}</components.MenuList>
    <div className={styles.connectorListFooter}>
      <button
        className={styles.requestNewConnectorBtn}
        onClick={() => props.selectProps.selectProps.onOpenRequestConnectorModal(props.selectProps.inputValue)}
      >
        <FontAwesomeIcon icon={faPlus} />
        <FormattedMessage id="connector.requestConnectorBlock" />
      </button>
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
    <div className={styles.stageLabel}>
      <FormattedMessage id={`connector.releaseStage.${releaseStage}`} defaultMessage={releaseStage} />
    </div>
  );
};

const Option: React.FC<DropDownOptionProps> = (props) => {
  return (
    <components.Option {...props}>
      <OptionView
        data-testid={props.data.label}
        isSelected={props.isSelected}
        isDisabled={props.isDisabled}
        isFocused={props.isFocused}
      >
        <div className={styles.connectorName}>
          {props.data.img || null}
          <Text size="lg">{props.label}</Text>
        </div>
        <StageLabel releaseStage={props.data.releaseStage} />
      </OptionView>
    </components.Option>
  );
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const SingleValue: React.FC<SingleValueProps<any>> = (props) => {
  return (
    <SingleValueView>
      {props.data.img && <SingleValueIcon>{props.data.img}</SingleValueIcon>}
      <div>
        <components.SingleValue className={styles.singleValueContent} {...props}>
          {props.data.label}
          <StageLabel releaseStage={props.data.releaseStage} />
        </components.SingleValue>
      </div>
    </SingleValueView>
  );
};

interface ConnectorServiceTypeControlProps {
  formType: "source" | "destination";
  availableServices: ConnectorDefinition[];
  isEditMode?: boolean;
  documentationUrl?: string;
  onChangeServiceType?: (id: string) => void;
  disabled?: boolean;
  selectedServiceId?: string;
}

const ConnectorServiceTypeControl: React.FC<ConnectorServiceTypeControlProps> = ({
  formType,
  isEditMode,
  onChangeServiceType,
  availableServices,
  documentationUrl,
  disabled,
  selectedServiceId,
}) => {
  const { formatMessage } = useIntl();
  const { openModal, closeModal } = useModalService();
  const { trackMenuOpen, trackNoOptionMessage, trackConnectorSelection } = useAnalyticsTrackFunctions(formType);

  const workspace = useCurrentWorkspace();
  const orderOverwrite = useExperiment("connector.orderOverwrite", {});
  const availableConnectorDefinitions = useAvailableConnectorDefinitions(availableServices, workspace);
  const sortedDropDownData = useMemo(
    () => getSortedDropdownDataUsingExperiment(availableConnectorDefinitions, orderOverwrite),
    [availableConnectorDefinitions, orderOverwrite]
  );

  const { setDocumentationUrl } = useDocumentationPanelContext();
  useEffect(() => setDocumentationUrl(documentationUrl ?? ""), [documentationUrl, setDocumentationUrl]);

  const getNoOptionsMessage = useCallback(
    ({ inputValue }: { inputValue: string }) => {
      trackNoOptionMessage(inputValue);
      return formatMessage({ id: "form.noConnectorFound" });
    },
    [formatMessage, trackNoOptionMessage]
  );

  const selectedService = React.useMemo(
    () => availableServices.find((s) => Connector.id(s) === selectedServiceId),
    [selectedServiceId, availableServices]
  );

  const handleSelect = useCallback(
    (item: DropDownOptionDataItem | null) => {
      if (item && onChangeServiceType) {
        onChangeServiceType(item.value);
        trackConnectorSelection(item.value, item.label || "");
      }
    },
    [onChangeServiceType, trackConnectorSelection]
  );

  const selectProps = useMemo(
    () => ({
      onOpenRequestConnectorModal: (input: string) =>
        openModal({
          title: formatMessage({ id: "connector.requestConnector" }),
          content: () => (
            <RequestConnectorModal
              connectorType={formType}
              workspaceEmail={workspace.email}
              searchedConnectorName={input}
              onClose={closeModal}
            />
          ),
        }),
    }),
    [closeModal, formType, formatMessage, openModal, workspace.email]
  );

  return (
    <>
      <ControlLabels
        label={formatMessage({
          id: `form.${formType}Type`,
        })}
      >
        <DropDown
          value={selectedServiceId}
          components={{
            MenuList: ConnectorList,
            Option,
            SingleValue,
          }}
          selectProps={selectProps}
          isDisabled={isEditMode || disabled}
          isSearchable
          placeholder={formatMessage({
            id: "form.selectConnector",
          })}
          options={sortedDropDownData}
          onChange={handleSelect}
          onMenuOpen={() => trackMenuOpen()}
          noOptionsMessage={getNoOptionsMessage}
          data-testid="serviceType"
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
