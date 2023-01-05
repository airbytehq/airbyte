import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useCallback, useMemo, useState } from "react";
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

import { ReleaseStage } from "core/request/AirbyteClient";
import { useModalService } from "hooks/services/Modal";
import styles from "views/Connector/ConnectorForm/components/Controls/ConnectorServiceTypeControl/ConnectorServiceTypeControl.module.scss";
import { useAnalyticsTrackFunctions } from "views/Connector/ConnectorForm/components/Controls/ConnectorServiceTypeControl/useAnalyticsTrackFunctions";
import { WarningMessage } from "views/Connector/ConnectorForm/components/WarningMessage";
import RequestConnectorModal from "views/Connector/RequestConnectorModal";

import { useGetSourceDefinitions } from "./useGetSourceDefinitions";
import { getSortedDropdownData } from "./utils";

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

interface SignupSourceDropdownProps {
  disabled?: boolean;
  email: string;
}

export const SignupSourceDropdown: React.FC<SignupSourceDropdownProps> = ({ disabled, email }) => {
  const { formatMessage } = useIntl();
  const { openModal, closeModal } = useModalService();
  const { trackMenuOpen, trackNoOptionMessage, trackConnectorSelection } = useAnalyticsTrackFunctions("source");

  const { data: availableSources } = useGetSourceDefinitions();

  const [sourceDefinitionId, setSourceDefinitionId] = useState<string>("");

  const onChangeServiceType = useCallback((sourceDefinitionId: string) => {
    setSourceDefinitionId(sourceDefinitionId);
    localStorage.setItem("exp-signup-selected-source-definition-id", sourceDefinitionId);
  }, []);

  const sortedDropDownData = useMemo(() => getSortedDropdownData(availableSources ?? []), [availableSources]);

  const getNoOptionsMessage = useCallback(
    ({ inputValue }: { inputValue: string }) => {
      trackNoOptionMessage(inputValue);
      return formatMessage({ id: "form.noConnectorFound" });
    },
    [formatMessage, trackNoOptionMessage]
  );

  const selectedService = React.useMemo(
    () => sortedDropDownData.find((s) => s.value === sourceDefinitionId),
    [sourceDefinitionId, sortedDropDownData]
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
              connectorType="source"
              workspaceEmail={email}
              searchedConnectorName={input}
              onClose={closeModal}
            />
          ),
        }),
    }),
    [closeModal, formatMessage, openModal, email]
  );

  if (!Boolean(sortedDropDownData.length)) {
    return null;
  }
  return (
    <>
      <ControlLabels
        label={formatMessage({
          id: "login.sourceSelector",
        })}
      >
        <DropDown
          value={sourceDefinitionId}
          components={{
            MenuList: ConnectorList,
            Option,
            SingleValue,
          }}
          selectProps={selectProps}
          isDisabled={disabled}
          isSearchable
          placeholder={formatMessage({
            id: "form.selectConnector",
          })}
          options={sortedDropDownData}
          onChange={handleSelect}
          onMenuOpen={trackMenuOpen}
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
