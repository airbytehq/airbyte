import { Form, Formik, useField } from "formik";
import merge from "lodash/merge";
import { useState } from "react";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { v4 as uuid } from "uuid";
import * as yup from "yup";

import { Button } from "components/ui/Button";
import { Modal, ModalBody, ModalFooter } from "components/ui/Modal";

import { Action, Namespace } from "core/analytics";
import { FormikPatch } from "core/form/FormikPatch";
import { useAnalyticsService } from "hooks/services/Analytics";

import styles from "./AddStreamButton.module.scss";
import { BuilderField } from "./BuilderField";
import { ReactComponent as PlusIcon } from "../../connection/ConnectionOnboarding/plusIcon.svg";
import { BuilderStream, DEFAULT_BUILDER_STREAM_VALUES } from "../types";

interface AddStreamValues {
  streamName: string;
  urlPath: string;
}

interface AddStreamButtonProps {
  onAddStream: (addedStreamNum: number) => void;
  button?: React.ReactElement;
  initialValues?: Partial<BuilderStream>;
  "data-testid"?: string;
}

export const AddStreamButton: React.FC<AddStreamButtonProps> = ({
  onAddStream,
  button,
  initialValues,
  "data-testid": testId,
}) => {
  const analyticsService = useAnalyticsService();
  const { formatMessage } = useIntl();
  const [isOpen, setIsOpen] = useState(false);
  const [streamsField, , helpers] = useField<BuilderStream[]>("streams");
  const numStreams = streamsField.value.length;

  const buttonClickHandler = () => {
    setIsOpen(true);
  };

  return (
    <>
      {button ? (
        React.cloneElement(button, {
          onClick: buttonClickHandler,
          "data-testid": testId,
        })
      ) : (
        <Button className={styles.addButton} onClick={buttonClickHandler} icon={<PlusIcon />} data-testid={testId} />
      )}
      {isOpen && (
        <Formik
          initialValues={{ streamName: "", urlPath: "" }}
          onSubmit={(values: AddStreamValues) => {
            const id = uuid();
            helpers.setValue([
              ...streamsField.value,
              merge({}, DEFAULT_BUILDER_STREAM_VALUES, {
                ...initialValues,
                name: values.streamName,
                urlPath: values.urlPath,
                id,
              }),
            ]);
            setIsOpen(false);
            onAddStream(numStreams);
            if (initialValues) {
              analyticsService.track(Namespace.CONNECTOR_BUILDER, Action.STREAM_COPY, {
                actionDescription: "Existing stream copied into a new stream",
                existing_stream_id: initialValues.id,
                existing_stream_name: initialValues.name,
                new_stream_id: id,
                new_stream_name: values.streamName,
                new_stream_url_path: values.urlPath,
              });
            } else {
              analyticsService.track(Namespace.CONNECTOR_BUILDER, Action.STREAM_CREATE, {
                actionDescription: "New stream created from the Add Stream button",
                stream_id: id,
                stream_name: values.streamName,
                url_path: values.urlPath,
              });
            }
          }}
          validationSchema={yup.object().shape({
            streamName: yup.string().required("form.empty.error"),
            urlPath: yup.string().required("form.empty.error"),
          })}
        >
          <>
            <FormikPatch />
            <Modal
              size="sm"
              title={<FormattedMessage id="connectorBuilder.addStreamModal.title" />}
              onClose={() => {
                setIsOpen(false);
              }}
            >
              <Form>
                <ModalBody className={styles.body}>
                  <BuilderField
                    path="streamName"
                    type="string"
                    label={formatMessage({ id: "connectorBuilder.addStreamModal.streamNameLabel" })}
                    tooltip={formatMessage({ id: "connectorBuilder.addStreamModal.streamNameTooltip" })}
                  />
                  <BuilderField
                    path="urlPath"
                    type="string"
                    label={formatMessage({ id: "connectorBuilder.addStreamModal.urlPathLabel" })}
                    tooltip={formatMessage({ id: "connectorBuilder.addStreamModal.urlPathTooltip" })}
                  />
                </ModalBody>
                <ModalFooter>
                  <Button
                    variant="secondary"
                    type="reset"
                    onClick={() => {
                      setIsOpen(false);
                    }}
                  >
                    <FormattedMessage id="form.cancel" />
                  </Button>
                  <Button type="submit">
                    <FormattedMessage id="form.create" />
                  </Button>
                </ModalFooter>
              </Form>
            </Modal>
          </>
        </Formik>
      )}
    </>
  );
};
