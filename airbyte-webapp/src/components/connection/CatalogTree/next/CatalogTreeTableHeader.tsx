import { faGear } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { useFormikContext } from "formik";
import React from "react";
import { FormattedMessage } from "react-intl";

import { FormikConnectionFormValues } from "components/connection/ConnectionForm/formConfig";
import { Header } from "components/SimpleTableComponents";
import { Button } from "components/ui/Button";
import { CheckBox } from "components/ui/CheckBox";
import { Text } from "components/ui/Text";
import { InfoTooltip, TooltipLearnMoreLink } from "components/ui/Tooltip";

import { NamespaceDefinitionType } from "core/request/AirbyteClient";
import { useNewTableDesignExperiment } from "hooks/connection/useNewTableDesignExperiment";
import { useBulkEditService } from "hooks/services/BulkEdit/BulkEditService";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { useModalService } from "hooks/services/Modal";
import { links } from "utils/links";

import { CatalogTreeTableCell } from "./CatalogTreeTableCell";
import styles from "./CatalogTreeTableHeader.module.scss";
import {
  DestinationNamespaceFormValueType,
  DestinationNamespaceModal,
} from "../../DestinationNamespaceModal/DestinationNamespaceModal";
import {
  DestinationStreamNamesFormValueType,
  DestinationStreamNamesModal,
  StreamNameDefinitionValueType,
} from "../../DestinationStreamNamesModal/DestinationStreamNamesModal";

const HeaderCell: React.FC<React.PropsWithChildren<Parameters<typeof CatalogTreeTableCell>[0]>> = ({
  size,
  children,
}) => {
  return (
    <CatalogTreeTableCell size={size}>
      <Text size="sm" className={styles.cellText}>
        {children}
      </Text>
    </CatalogTreeTableCell>
  );
};

export const CatalogTreeTableHeader: React.FC = () => {
  const { mode } = useConnectionFormService();
  const { openModal, closeModal } = useModalService();
  const { onCheckAll, selectedBatchNodeIds, allChecked } = useBulkEditService();
  const formikProps = useFormikContext<FormikConnectionFormValues>();
  const isNewTableDesignEnabled = useNewTableDesignExperiment();

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
    <Header className={classNames(styles.headerContainer, { [styles.newTable]: !!isNewTableDesignEnabled })}>
      <CatalogTreeTableCell size="small" className={styles.checkboxCell}>
        {mode !== "readonly" && (
          <CheckBox
            onChange={onCheckAll}
            indeterminate={selectedBatchNodeIds.length > 0 && !allChecked}
            checked={allChecked}
          />
        )}
      </CatalogTreeTableCell>
      <HeaderCell size="small">
        <FormattedMessage id="sources.sync" />
      </HeaderCell>
      {/* <TextCell>
        <FormattedMessage id="form.fields" />
      </TextCell> */}
      <HeaderCell>
        <FormattedMessage id="form.namespace" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.sourceNamespace.info" />
        </InfoTooltip>
      </HeaderCell>
      <HeaderCell>
        <FormattedMessage id="form.streamName" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.sourceStreamName.info" />
        </InfoTooltip>
      </HeaderCell>
      <HeaderCell size="large">
        <FormattedMessage id="form.syncMode" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.syncType.info" />
          <TooltipLearnMoreLink url={links.syncModeLink} />
        </InfoTooltip>
      </HeaderCell>
      <HeaderCell>
        <FormattedMessage id="form.cursorField" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.cursor.info" />
        </InfoTooltip>
      </HeaderCell>
      <HeaderCell>
        <FormattedMessage id="form.primaryKey" />
        <InfoTooltip>
          <FormattedMessage id="connectionForm.primaryKey.info" />
        </InfoTooltip>
      </HeaderCell>
      <CatalogTreeTableCell size="xsmall" />
      <HeaderCell>
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
      </HeaderCell>
      <HeaderCell>
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
      </HeaderCell>
    </Header>
  );
};
