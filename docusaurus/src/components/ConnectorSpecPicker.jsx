import { useEffect, useMemo, useState } from "react";
import useBaseUrl from "@docusaurus/useBaseUrl";
import { SpecSchema } from "./SpecSchema";
import styles from "./ConnectorSpecPicker.module.css";

const DOCS_SITE_PREFIX = "https://docs.airbyte.com";

const toDocsHref = (documentationUrl) =>
  documentationUrl.startsWith(DOCS_SITE_PREFIX)
    ? documentationUrl.slice(DOCS_SITE_PREFIX.length)
    : documentationUrl;

const CONNECTOR_TYPES = [
  { value: "all", label: "All" },
  { value: "source", label: "Sources" },
  { value: "destination", label: "Destinations" },
];

export const ConnectorSpecPicker = ({ connectorType: fixedType, compact }) => {
  const specsBaseUrl = useBaseUrl("/connector-specs/");
  const [index, setIndex] = useState(null);
  const [indexError, setIndexError] = useState(null);
  const [connectorType, setConnectorType] = useState(fixedType || "all");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState(null);
  const [spec, setSpec] = useState(null);
  const [specError, setSpecError] = useState(null);

  useEffect(() => {
    let active = true;
    fetch(`${specsBaseUrl}index.json`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }
        return response.json();
      })
      .then((entries) => {
        if (active) {
          setIndex(entries);
        }
      })
      .catch((error) => {
        if (active) {
          setIndexError(error.message);
        }
      });
    return () => {
      active = false;
    };
  }, [specsBaseUrl]);

  useEffect(() => {
    if (!selected) {
      return undefined;
    }

    let active = true;
    setSpec(null);
    setSpecError(null);
    fetch(`${specsBaseUrl}${selected.definitionId}.json`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }
        return response.json();
      })
      .then((connectorSpec) => {
        if (active) {
          setSpec(connectorSpec);
        }
      })
      .catch((error) => {
        if (active) {
          setSpecError(error.message);
        }
      });
    return () => {
      active = false;
    };
  }, [selected, specsBaseUrl]);

  const matches = useMemo(() => {
    if (!index) {
      return [];
    }
    const normalizedQuery = query.trim().toLowerCase();
    return index.filter((entry) => {
      if (connectorType !== "all" && entry.connector_type !== connectorType) {
        return false;
      }
      if (!normalizedQuery) {
        return true;
      }
      return (
        entry.name.toLowerCase().includes(normalizedQuery) ||
        entry.dockerRepository.toLowerCase().includes(normalizedQuery)
      );
    });
  }, [index, connectorType, query]);

  if (indexError) {
    return (
      <p>
        The connector list could not be loaded ({indexError}). Browse the{" "}
        <a href="/integrations">connector catalog</a> instead.
      </p>
    );
  }

  return (
    <div>
      <div className={styles.controls}>
        <input
          type="search"
          className={styles.search}
          placeholder={
            index
              ? `Search ${
                  fixedType
                    ? `${index.filter((entry) => entry.connector_type === fixedType).length} ${fixedType}s`
                    : `${index.length} connectors`
                }`
              : "Loading connectors..."
          }
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          disabled={!index}
        />
        <div className={styles.types}>
          {!fixedType &&
            CONNECTOR_TYPES.map((type) => (
              <button
                key={type.value}
                type="button"
                className={
                  type.value === connectorType
                    ? `${styles.typeButton} ${styles.typeButtonActive}`
                    : styles.typeButton
                }
                onClick={() => setConnectorType(type.value)}
              >
                {type.label}
              </button>
            ))}
        </div>
      </div>

      {index && matches.length === 0 && (
        <p className={styles.empty}>No connectors match that search.</p>
      )}

      {matches.length > 0 && (
        <ul className={styles.results}>
          {matches.map((entry) => (
            <li key={entry.definitionId}>
              <button
                type="button"
                className={
                  entry.definitionId === selected?.definitionId
                    ? `${styles.result} ${styles.resultActive}`
                    : styles.result
                }
                onClick={() => setSelected(entry)}
              >
                <span className={styles.resultName}>{entry.name}</span>
                <span className={styles.resultType}>
                  {entry.connector_type}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}

      {selected && (
        <div className={styles.spec}>
          {compact ? (
            <p className={styles.compactName}>{selected.name}</p>
          ) : (
            <h2>{selected.name}</h2>
          )}
          <p>
            <code>{selected.dockerRepository}</code>
            {selected.documentationUrl && (
              <>
                {" \u00b7 "}
                <a href={toDocsHref(selected.documentationUrl)}>
                  Connector documentation
                </a>
              </>
            )}
          </p>
          {specError && (
            <p>
              The configuration fields for {selected.name} could not be loaded (
              {specError}).
            </p>
          )}
          {!spec && !specError && <p>Loading configuration fields...</p>}
          {spec && <SpecSchema specJSON={JSON.stringify(spec)} />}
        </div>
      )}
    </div>
  );
};
