import classNames from "classnames";
import { FormattedMessage } from "react-intl";

import { Tooltip } from "components/ui/Tooltip";

import styles from "./StepsIndicator.module.scss";

interface Step {
  id: string;
  name: string;
}

interface StepIndicatorProps {
  step: Step;
  isCurrent: boolean;
  isCompleted: boolean;
}

interface StepsIndicatorProps {
  steps: Step[];
  activeStep: string;
  className?: string;
}

const StepIndicator: React.FC<StepIndicatorProps> = ({ step, isCurrent, isCompleted }) => {
  return (
    <Tooltip
      containerClassName={styles.tooltip}
      control={
        <span
          aria-label={step.name}
          aria-current={isCurrent ? "step" : undefined}
          className={classNames(styles.step, { [styles.current]: isCurrent, [styles.completed]: isCompleted })}
        />
      }
    >
      {step.name} {isCurrent && <FormattedMessage id="ui.stepIndicator.currentStep" />}
    </Tooltip>
  );
};

export const StepsIndicator: React.FC<StepsIndicatorProps> = ({ className, steps, activeStep }) => {
  const activeIndex = steps.findIndex((step) => step.id === activeStep);
  return (
    <div className={classNames(className, styles.steps)}>
      {steps.map((step, index) => (
        <StepIndicator step={step} isCurrent={activeStep === step.id} isCompleted={index < activeIndex} />
      ))}
    </div>
  );
};
