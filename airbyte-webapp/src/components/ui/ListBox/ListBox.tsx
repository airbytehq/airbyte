import { Listbox } from "@headlessui/react";
import classNames from "classnames";
import React from "react";

import { ReactComponent as CaretDownIcon } from "./CaretDownIcon.svg";
import styles from "./ListBox.module.scss";

export interface ListBoxControlButtonProps<T> {
  selectedOption: Option<T>;
}

const DefaultControlButton = <T,>({ selectedOption }: ListBoxControlButtonProps<T>) => {
  return (
    <>
      {selectedOption.label}
      <CaretDownIcon className={styles.caret} />
    </>
  );
};

export interface Option<T> {
  label: string;
  value: T;
  icon?: React.ReactNode;
}

interface ListBoxProps<IsMultiple extends boolean, T extends IsMultiple extends true ? any[] : any> {
  className?: string;
  multiple?: IsMultiple;
  optionClassName?: string;
  selectedOptionClassName?: string;
  options: Array<Option<IsMultiple extends true ? T[number] : T>>;
  selectedValue: T;
  onSelect: (selectedValue: T) => void;
  buttonClassName?: string;
  controlButton?: React.ComponentType<ListBoxControlButtonProps<T>>;
}

export const ListBox = <IsMultiple extends boolean, T extends IsMultiple extends true ? any[] : any>({
  className,
  multiple,
  options,
  selectedValue,
  onSelect,
  buttonClassName,
  controlButton: ControlButton = DefaultControlButton,
  optionClassName,
  selectedOptionClassName,
}: ListBoxProps<IsMultiple, T>) => {
  const selectedOption = options.find((option) => option.value === selectedValue) ?? {
    label: String(selectedValue),
    value: selectedValue,
  };

  return (
    <div className={className}>
      <Listbox value={selectedValue} onChange={onSelect} multiple={multiple}>
        <Listbox.Button className={classNames(buttonClassName, styles.button)}>
          <ControlButton selectedOption={selectedOption} />
        </Listbox.Button>
        {/* wrap in div to make `position: absolute` on Listbox.Options result in correct vertical positioning */}
        <div className={styles.optionsContainer}>
          <Listbox.Options className={classNames(styles.optionsMenu)}>
            {options.map(({ label, value, icon }) => (
              <Listbox.Option key={label} value={value} className={classNames(styles.option, optionClassName)}>
                {({ active, selected }) => (
                  <div
                    className={classNames(styles.optionValue, selected && selectedOptionClassName, {
                      [styles.active]: active,
                      [styles.selected]: selected,
                    })}
                  >
                    {icon && <span className={styles.icon}>{icon}</span>}
                    <span className={styles.label}>{label}</span>
                  </div>
                )}
              </Listbox.Option>
            ))}
          </Listbox.Options>
        </div>
      </Listbox>
    </div>
  );
};
