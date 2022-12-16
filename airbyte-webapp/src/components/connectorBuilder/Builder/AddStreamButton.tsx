import { Form, Formik, useField } from "formik";
import { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { Button } from "components/ui/Button";
import { Modal, ModalBody, ModalFooter } from "components/ui/Modal";

import { FormikPatch } from "core/form/FormikPatch";

import { ReactComponent as PlusIcon } from "../../connection/ConnectionOnboarding/plusIcon.svg";
import { BuilderStream } from "../types";
import styles from "./AddStreamButton.module.scss";
import { BuilderField } from "./BuilderField";

interface AddStreamValues {
  streamName: string;
  urlPath: string;
}

interface AddStreamButtonProps {
  onAddStream: (addedStreamNum: number) => void;
}

export const AddStreamButton: React.FC<AddStreamButtonProps> = ({ onAddStream }) => {
  const { formatMessage } = useIntl();
  const [isOpen, setIsOpen] = useState(false);
  const [streamsField, , helpers] = useField<BuilderStream[]>("streams");
  const numStreams = streamsField.value.length;

  return (
    <>
      <Button
        className={styles.addButton}
        onClick={() => {
          setIsOpen(true);
        }}
        icon={<PlusIcon />}
      />
      {isOpen && (
        <Formik
          initialValues={{ streamName: "", urlPath: "" }}
          onSubmit={(values: AddStreamValues) => {
            helpers.setValue([
              ...streamsField.value,
              {
                name: values.streamName,
                urlPath: values.urlPath,
                fieldPointer: [],
                httpMethod: "GET",
                requestOptions: {
                  requestParameters: [],
                  requestHeaders: [],
                  requestBody: [],
                },
              },
            ]);
            setIsOpen(false);
            onAddStream(numStreams);
          }}
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
                    type="text"
                    label={formatMessage({ id: "connectorBuilder.addStreamModal.streamNameLabel" })}
                    tooltip={formatMessage({ id: "connectorBuilder.addStreamModal.streamNameTooltip" })}
                  />
                  <BuilderField
                    path="urlPath"
                    type="text"
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
