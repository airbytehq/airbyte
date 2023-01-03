import { faPlus, faUser } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useField } from "formik";
import { useState } from "react";

import { ListBox, ListBoxControlButtonProps, Option } from "components/ui/ListBox";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { getInferredInputs } from "../types";
import { BuilderField, BuilderFieldProps } from "./BuilderField";
import styles from "./BuilderFieldWithInputs.module.scss";
import { InputForm, newInputInEditing } from "./InputsForm";

export const BuilderFieldWithInputs: React.FC<BuilderFieldProps> = (props) => {
  const [field, , helpers] = useField(props.path);

  return (
    <BuilderField {...props} adornment={<UserInputHelper setValue={helpers.setValue} currentValue={field.value} />} />
  );
};

export const UserInputHelper = ({
  setValue,
  currentValue,
}: {
  setValue: (value: string) => void;
  currentValue: string;
}) => {
  const [modalOpen, setModalOpen] = useState(false);
  const { builderFormValues } = useConnectorBuilderState();
  const options: Array<Option<string | undefined>> = [
    ...builderFormValues.inputs,
    ...getInferredInputs(builderFormValues),
  ].map((input) => ({
    label: input.definition.title || input.key,
    value: input.key,
  }));
  options.push({ value: undefined, label: "Add new input", icon: <FontAwesomeIcon icon={faPlus} /> });
  return (
    <>
      <ListBox<string | undefined>
        buttonClassName={styles.buttonWrapper}
        optionClassName={styles.option}
        selectedOptionClassName={styles.selectedOption}
        controlButton={UserInputHelperControlButton}
        selectedValue={undefined}
        onSelect={(selectedValue) => {
          if (selectedValue) {
            setValue(`${currentValue || ""}{{ config['${selectedValue}'] }}`);
          } else {
            setModalOpen(true);
          }
        }}
        options={options}
      />
      {modalOpen && (
        <InputForm
          inputInEditing={newInputInEditing()}
          onClose={(newInput) => {
            setModalOpen(false);
            if (!newInput) {
              return;
            }
            setValue(`${currentValue}{{ config['${newInput.key}'] }}`);
          }}
        />
      )}
    </>
  );
};

const UserInputHelperControlButton: React.FC<ListBoxControlButtonProps<string | undefined>> = () => {
  return <FontAwesomeIcon icon={faUser} />;
};
