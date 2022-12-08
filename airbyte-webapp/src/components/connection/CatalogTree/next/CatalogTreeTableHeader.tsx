import { faGear } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useFormikContext } from "formik";
import React from "react";
import { FormattedMessage } from "react-intl";

import { Cell, Header } from "components/SimpleTableComponents";
import { Button } from "components/ui/Button";
import { CheckBox } from "components/ui/CheckBox";
import { Text } from "components/ui/Text";
import { InfoTooltip, TooltipLearnMoreLink } from "components/ui/Tooltip";

import { NamespaceDefinitionType } from "core/request/AirbyteClient";
import { useBulkEditService } from "hooks/services/BulkEdit/BulkEditService";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { useModalService } from "hooks/services/Modal";
import { links } from "utils/links";
import { FormikConnectionFormValues } from "views/Connection/ConnectionForm/formConfig";

import {
  DestinationNamespaceFormValueType,
  DestinationNamespaceModal,
} from "../../DestinationNamespaceModal/DestinationNamespaceModal";
import {
  DestinationStreamNamesFormValueType,
  DestinationStreamNamesModal,
  StreamNameDefinitionValueType,
} from "../../DestinationStreamNamesModal/DestinationStreamNamesModal";
import styles from "./CatalogTreeTableHeader.module.scss";

const TextCell: React.FC<React.PropsWithChildren<{ flex?: number }>> = ({ flex, children }) => {
  return (
    <Cell flex={flex}>
      <Text size="sm" className={styles.cellText}>
        {children}
      </Text>
    </Cell>
  );
};

export const CatalogTreeTableHeader: React.FC = () => {
  const { mode } = useConnectionFormService();
  const { openModal, closeModal } = useModalService();
  const { onCheckAll, selectedBatchNodeIds, allChecked } = useBulkEditService();
  const formikProps = useFormikContext<FormikConnectionFormValues>();

  const destinationNamespaceChange = (value: DestinationNamespaceFormValueType) => {
    formikProps.setFieldValue("namespaceDefinition", value.namespaceDefinition);

    if (value.namespaceDefinition === NamespaceDefinitionType.customformat) {
      formikProps.setFieldValue("namespaceFormat", value.namespaceFormat);
    }
  };

  const destinationStreamNamesChange = (value: DestinationStreamNamesFormValueType) => {
    formikProps.setFieldValue(
      "prefix",
      value.streamNameDefinition === StreamNameDefinitionValueType.Prefix ? value.prefix : ""
    );
  };

  return (
    <Header className={styles.headerContainer}>
      <div className={styles.checkboxCell}>
        {mode !== "readonly" && (
          <CheckBox
            onChange={onCheckAll}
            indeterminate={selectedBatchNodeIds.length > 0 && !allChecked}
            checked={allChecked}
          />
        )}
      </div>
      <TextCell flex={0.5}>
        <FormattedMessage id="sources.sync" />
      </TextCell>
      {/* <TextCell>
        <FormattedMessage id="form.fields" />
      </TextCell> */}
      <TextCell flex={1}>
        <FormattedMessage id="form.namespace" />
      </TextCell>
      <TextCell flex={1}>
        <FormattedMessage id="form.streamName" />
      </TextCell>
      <TextCell flex={2}>
        <FormattedMessage id="form.syncMode" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.syncType.info" />
          <TooltipLearnMoreLink url={links.syncModeLink} />
        </InfoTooltip>
      </TextCell>
      <TextCell flex={1}>
        <FormattedMessage id="form.cursorField" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.cursor.info" />
        </InfoTooltip>
      </TextCell>
      <TextCell flex={1}>
        <FormattedMessage id="form.primaryKey" />
      </TextCell>
      <div className={styles.arrowPlaceholder} />
      <TextCell flex={1}>
        <FormattedMessage id="form.namespace" />
        <Button
          type="button"
          variant="clear"
          onClick={() =>
            openModal({
              size: "lg",
              title: <FormattedMessage id="connectionForm.modal.destinationNamespace.title" />,
              content: () => (
                <DestinationNamespaceModal
                  initialValues={{
                    namespaceDefinition: formikProps.values.namespaceDefinition,
                    namespaceFormat: formikProps.values.namespaceFormat,
                  }}
                  onCloseModal={closeModal}
                  onSubmit={destinationNamespaceChange}
                />
              ),
            })
          }
        >
          <FontAwesomeIcon icon={faGear} />
        </Button>
      </TextCell>
      <TextCell flex={1}>
        <FormattedMessage id="form.streamName" />
        <Button
          type="button"
          variant="clear"
          onClick={() =>
            openModal({
              size: "sm",
              title: <FormattedMessage id="connectionForm.modal.destinationStreamNames.title" />,
              content: () => (
                <DestinationStreamNamesModal
                  initialValues={{
                    prefix: formikProps.values.prefix,
                  }}
                  onCloseModal={closeModal}
                  onSubmit={destinationStreamNamesChange}
                />
              ),
            })
          }
        >
          <FontAwesomeIcon icon={faGear} />
        </Button>
      </TextCell>
    </Header>
  );
};
