import { useEffect, useRef } from "react";
import { useLocation } from "@docusaurus/router";

export function HashRedirect({ redirects }) {
  const location = useLocation();
  const didRedirect = useRef(false);

  useEffect(() => {
    if (!location.hash || didRedirect.current) return;

    const id = decodeURIComponent(location.hash.slice(1));
    const target = redirects[id];
    if (
      target &&
      location.pathname !== target &&
      !document.getElementById(id)
    ) {
      didRedirect.current = true;
      window.location.replace(`${target}#${id}`);
    }
  }, [location.hash, location.pathname, redirects]);

  return null;
}

export default HashRedirect;
