import { Listbox } from "@headlessui/react";
import classNames from "classnames";
import React from "react";

import styles from "./ListBox.module.scss";

interface ListBoxProps {
  className?: string;
  values: string[];
  selectedValue: string;
  onSelect: (selected: string) => void;
  buttonClassName?: string;
  buttonContent?: (value: string) => React.ReactNode;
  optionContent?: (value: string) => React.ReactNode;
}

export const ListBox: React.FC<ListBoxProps> = ({
  className,
  values,
  selectedValue,
  onSelect,
  buttonClassName,
  buttonContent,
  optionContent,
}) => {
  return (
    <div className={className}>
      <Listbox value={selectedValue} onChange={onSelect}>
        <Listbox.Button className={classNames(buttonClassName, styles.button)}>
          {buttonContent ? buttonContent(selectedValue) : selectedValue}
        </Listbox.Button>
        {/* wrap in div to make `position: absolute` on Listbox.Options result in correct vertical positioning */}
        <div className={styles.optionsContainer}>
          <Listbox.Options className={classNames(styles.optionsMenu)}>
            {values.map((value) => (
              <Listbox.Option key={value} value={value} className={styles.option}>
                {({ active, selected }) => (
                  <div
                    className={classNames(styles.optionValue, { [styles.active]: active, [styles.selected]: selected })}
                  >
                    {optionContent ? optionContent(value) : value}
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
