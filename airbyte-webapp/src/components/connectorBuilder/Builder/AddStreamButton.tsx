import { Formik } from "formik";
import { useState } from "react";

import { Button } from "components/ui/Button";
import { Modal, ModalBody, ModalFooter } from "components/ui/Modal";

import { FormikPatch } from "./Builder";
import { BuilderField } from "./BuilderField";

interface AddStreamValues {
  streamName: string;
  urlPath: string;
}

export const AddStreamButton: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button onClick={() => setIsOpen(true)}>Add stream</button>
      {isOpen && (
        <Modal size="sm" title="New stream" onClose={() => setIsOpen(false)}>
          <Formik
            initialValues={{ streamName: "", urlPath: "" }}
            onSubmit={(values: AddStreamValues) => {
              console.log(values);
              setIsOpen(false);
            }}
          >
            <>
              <FormikPatch />
              <ModalBody>
                <BuilderField path="streamName" type="text" label="Stream name" tooltip="Name of the new stream" />
                <BuilderField
                  path="urlPath"
                  type="text"
                  label="URL Path"
                  tooltip="URL path of the endpoint for this stream"
                />
              </ModalBody>
              <ModalFooter>
                <Button type="submit">Create</Button>
              </ModalFooter>
            </>
          </Formik>
        </Modal>
      )}
    </>
  );
};
