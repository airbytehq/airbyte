import classNames from "classnames";
import { Form, Formik, useFormikContext } from "formik";
import { useState } from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { Heading } from "components/ui/Heading";
import { Modal, ModalBody, ModalFooter } from "components/ui/Modal";

import { ReactComponent as PlusIcon } from "../../connection/ConnectionOnboarding/plusIcon.svg";
import styles from "./AddStreamButton.module.scss";
import { FormikPatch } from "./Builder";
import { BuilderField } from "./BuilderField";

interface AddStreamValues {
  streamName: string;
  urlPath: string;
}

interface AddStreamButtonProps {
  className?: string;
  numStreams: number;
  onAddStream: (addedStreamNum: number, addedStreamName: string) => void;
}

export const AddStreamButton: React.FC<AddStreamButtonProps> = ({ className, numStreams, onAddStream }) => {
  const [isOpen, setIsOpen] = useState(false);
  const { setFieldValue } = useFormikContext();

  return (
    <>
      <Button
        className={classNames(className, styles.addButton)}
        onClick={() => {
          setIsOpen(true);
        }}
        icon={<PlusIcon className={styles.plus} />}
      />
      {isOpen && (
        <Formik
          initialValues={{ streamName: "", urlPath: "" }}
          onSubmit={(values: AddStreamValues) => {
            setFieldValue(`streams[${numStreams}]`, {
              name: values.streamName,
              urlPath: values.urlPath,
              fieldPointer: [],
              httpMethod: "GET",
            });
            setIsOpen(false);
            onAddStream(numStreams, values.streamName);
          }}
        >
          <>
            <FormikPatch />
            <Modal
              size="sm"
              title={
                <Heading as="h1" size="sm">
                  <FormattedMessage id="connectorBuilder.newStream" />
                </Heading>
              }
              onClose={() => {
                setIsOpen(false);
              }}
            >
              <Form>
                <ModalBody className={styles.body}>
                  <BuilderField path="streamName" type="text" label="Stream name" tooltip="Name of the new stream" />
                  <BuilderField
                    path="urlPath"
                    type="text"
                    label="URL Path"
                    tooltip="URL path of the endpoint for this stream"
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
