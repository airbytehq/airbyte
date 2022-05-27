import { Switch } from "@headlessui/react";
import classnames from "classnames";

import styles from "./HeadlessSwitch.module.scss";

interface SwitchProps {
  small?: boolean;
  loading?: boolean;
  disabled?: boolean;
  checked?: boolean;
  onChange?: (checked: boolean) => void;
  id?: string;
}

export const HeadlessSwitch: React.FC<SwitchProps> = ({
  checked,
  onChange = () => {
    return;
  },
  small,
  loading,
  disabled,
}) => {
  const switchStyle = classnames(styles.switch, {
    [styles.small]: small,
    [styles.loading]: loading,
    [styles.checked]: checked,
  });
  const spanStyle = classnames(styles.slider, {
    [styles.small]: small,
    [styles.loading]: loading,
  });

  return (
    <Switch checked={!!checked} onChange={onChange} className={switchStyle} disabled={disabled}>
      <span className={spanStyle} />
    </Switch>
  );
};
