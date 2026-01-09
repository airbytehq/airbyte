import {
  Combobox,
  ComboboxButton,
  ComboboxInput,
  ComboboxOption,
  ComboboxOptions,
} from "@headlessui/react";
import sourceConfigsDataRaw from "@site/src/data/source-configs-dereferenced.json";
import styles from "./index.module.css";
import { useState, useMemo } from "react";
import { faChevronDown } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import parse, { HTMLReactParserOptions, Element, DOMNode, Text } from 'html-react-parser';
import { ConfigSchemaProps, SourceConfig, EndpointData, OptionalEndpointData } from './types';

const sourceConfigsData = sourceConfigsDataRaw as SourceConfig[];

/**
 * Parse HTML description and convert elements to React components
 * Supports links, bold, italic, and other common HTML elements
 * Links open in new tabs with proper security attributes
 */
const parseHtmlDescription = (html: string) => {
  const options: HTMLReactParserOptions = {
    replace: (domNode: DOMNode) => {
      if (domNode instanceof Element && domNode.name === "a") {
        console.log("Parsing anchor element:", domNode);
        const href = domNode.attribs?.href;
        if (href) {
          return (
            <a href={href} target="_blank" rel="noopener noreferrer">
              {(domNode.children[0] as Text).data || href}
            </a>
          );
        }
      }
      // Return undefined to use the default rendering for non-anchor elements
      return undefined;
    },
  };

  const result = parse(html, options);
  console.log("Parsing HTML description:", result);
  // Ensure we always return an array for consistent rendering
  return Array.isArray(result) ? result : [result];
};

/**
 * Component to display configuration fields based on selected source type
 * Uses OpenAPI plugin classnames for perfect visual consistency
 */
const ConfigurationFields = ({
  selectedSourceId,
  configSchema,
}: ConfigSchemaProps) => {
  const selectedConfig = configSchema.oneOf?.find(
    (config) => config.title === selectedSourceId,
  );

  if (!selectedConfig) {
    return null;
  }

  const requiredFields = selectedConfig.required || [];
  const properties = selectedConfig.properties || {};

  // Sort properties: required first, then optional
  const sortedEntries = Object.entries(properties).sort(([nameA], [nameB]) => {
    const aRequired = requiredFields.includes(nameA);
    const bRequired = requiredFields.includes(nameB);
    if (aRequired === bRequired) return 0;
    return aRequired ? -1 : 1;
  });

  return (
    <ul style={{ marginLeft: "1rem", listStyle: "none", padding: 0 }}>
      <div className="openapi-schema__list-item">
        <div>
          <span className="openapi-schema__container">
            <strong className="openapi-schema__property">properties</strong>
            <span className="openapi-schema__name">object</span>
          </span>
        </div>
      </div>

      {sortedEntries.map(([fieldName, fieldSchema]) => (
        <div key={fieldName} className="openapi-schema__list-item">
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <span className="openapi-schema__container">
              <strong className="openapi-schema__property">{fieldName}</strong>
              <span className="openapi-schema__name">
                {fieldSchema.title || fieldSchema.type}
              </span>
            </span>
            {requiredFields.includes(fieldName) && (
              <span className="openapi-schema__required">required</span>
            )}
          </div>
          {fieldSchema.description && (
            <p>{parseHtmlDescription(fieldSchema.description)}</p>
          )}
        </div>
      ))}
    </ul>
  );
};

export const SourceConfiguration = ({ endpointData }: { endpointData: OptionalEndpointData }) => {
  const [sourceConfigs] = useState<SourceConfig[]>(sourceConfigsData);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSource, setSelectedSource] = useState<SourceConfig | null>(
    sourceConfigsData.length > 0 ? sourceConfigsData[0] : null,
  );

  const filteredSources = useMemo(() => {
    if (!searchQuery.trim()) {
      return sourceConfigs;
    }
    const query = searchQuery.toLowerCase();
    return sourceConfigs.filter(
      (source) =>
        source.displayName.toLowerCase().includes(query) ||
        source.id.toLowerCase().includes(query),
    );
  }, [searchQuery, sourceConfigs]);

  const handleSourceSelect = (source: SourceConfig) => {
    setSelectedSource(source);
  };

  // Build configurationSchema from sourceConfigs data
  const configurationSchema = {
    oneOf: sourceConfigs.map(config => ({
      title: config.id,
      ...config.schema
    }))
  };

  return (
    <>
      {sourceConfigs.length > 0 && (
        <>
          {/* Combobox for source selection */}
          <Combobox
            immediate
            value={selectedSource}
            onChange={handleSourceSelect}
            onClose={() => setSearchQuery("")}
          >
            <div className={styles.comboboxWrapper}>
              <ComboboxInput
                id="source-combobox"
                className={styles.input}
                placeholder="Search sources..."
                displayValue={(source: SourceConfig | null) => source?.id ?? ""}
                onChange={(event: React.ChangeEvent<HTMLInputElement>) => setSearchQuery(event.target.value)}
                autoComplete="off"
              />
              <ComboboxButton className={styles.dropdownButton}>
                <FontAwesomeIcon icon={faChevronDown} />
              </ComboboxButton>
            </div>

            <ComboboxOptions className={styles.dropdown} anchor="bottom">
              {filteredSources.length === 0 ? (
                <div className={styles.noResults}>
                  {searchQuery
                    ? `No sources found for "${searchQuery}"`
                    : "No sources available"}
                </div>
              ) : (
                filteredSources.map((source) => (
                  <ComboboxOption
                    key={source.id}
                    value={source}
                    className={({ active, selected }: { active: boolean; selected: boolean }) =>
                      `${styles.option} ${active ? styles.active : ""} ${
                        selected ? styles.selected : ""
                      }`
                    }
                  >
                    <span className={styles.optionId}>{source.id}</span>
                  </ComboboxOption>
                ))
              )}
            </ComboboxOptions>
          </Combobox>

          {/* Display configuration schema properties for selected source */}

          {/* Display required properties for selected source */}
          {selectedSource && configurationSchema.oneOf && (
            <ConfigurationFields
              selectedSourceId={selectedSource.id}
              configSchema={configurationSchema}
            />
          )}
        </>
      )}
    </>
  );
};
