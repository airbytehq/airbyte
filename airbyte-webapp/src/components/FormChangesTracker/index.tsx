import { useLayoutEffect, useMemo } from "react";
import { uniqueId } from "lodash";
import { useLocation } from "react-router-dom";

import { useChangedFormsById } from "hooks/useDiscardFormChangesConfirmation";

interface Props {
  changed: boolean;
}

const FormChangesTracker: React.FC<Props> = ({ changed }) => {
  const location = useLocation();
  const [changedFormsById, setChangedFormsById] = useChangedFormsById();
  const id = useMemo(() => `${location.pathname}__${uniqueId("form_")}`, [location.pathname]);

  useLayoutEffect(() => {
    if (!!changedFormsById?.[id] !== changed) {
      setChangedFormsById({ ...changedFormsById, [id]: changed });
    }
  }, [id, changed, setChangedFormsById, changedFormsById]);

  return null;
};

export default FormChangesTracker;
