import links from "../data/yaml-reference-links.json";

const base =
  "/platform/connector-development/config-based/understanding-the-yaml-file/reference";
const components = new Set(links.definitions);

export function redirectLegacyHash(location) {
  if (location.pathname.replace(/\/$/, "") !== base) return;
  const match = /^#\/(definitions|variables|macros|filters)\/([^/]+)$/.exec(
    location.hash,
  );
  if (!match) return;
  const [, group, name] = match;
  if (group === "definitions") {
    if (components.has(name)) location.replace(`${base}/${name}`);
  } else if (links[group].includes(name)) {
    location.replace(`${base}/${group}#${name}`);
  }
}

export function onRouteDidUpdate() {
  redirectLegacyHash(window.location);
}

if (typeof window !== "undefined") {
  window.addEventListener("hashchange", () =>
    redirectLegacyHash(window.location),
  );
}
