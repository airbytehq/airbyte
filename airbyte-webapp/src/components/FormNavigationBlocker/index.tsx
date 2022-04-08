import { useLayoutEffect, useMemo } from "react";
import { uniqueId } from "lodash";
import { useLocation } from "react-router-dom";

import { useBlockingFormsById } from "hooks/useFormNavigationBlocking";

interface Props {
  block: boolean;
}

const FormNavigationBlocker: React.FC<Props> = ({ block }) => {
  const location = useLocation();
  const [blockingFormsById, setBlockingFormsById] = useBlockingFormsById();
  const id = useMemo(() => `${location.pathname}__${uniqueId("form_")}`, [location.pathname]);

  useLayoutEffect(() => {
    if (!!blockingFormsById?.[id] !== block) {
      setBlockingFormsById({ ...blockingFormsById, [id]: block });
    }
  }, [id, block, setBlockingFormsById, blockingFormsById]);

  return null;
};

export default FormNavigationBlocker;
