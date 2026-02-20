import {
  Combobox,
  ComboboxButton,
  ComboboxInput,
  ComboboxOption,
  ComboboxOptions,
} from "@headlessui/react";
import destinationConfigsDataRaw from "@site/src/data/destination-configs-dereferenced.json";
import styles from "./index.module.css";
import { useState, useMemo } from "react";
import { faChevronDown } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import parse, { HTMLReactParserOptions, Element, DOMNode, Text } from 'html-react-parser';
import { ConfigSchemaProps, DestinationConfig, OptionalEndpointData } from './types';

const destinationConfigsData = destinationConfigsDataRaw as DestinationConfig[];

const parseHtmlDescription = (html: string) => {
  const options: HTMLReactParserOptions = {
    replace: (domNode: DOMNode) => {
      if (domNode instanceof Element && domNode.name === "a") {
        const href = domNode.attribs?.href;
        if (href) {
          return (
            <a href={href} target="_blank" rel="noopener noreferrer">
              {(domNode.children[0] as Text).data || href}
            </a>
          );
        }
      }
      return undefined;
    },
  };

  const result = parse(html, options);
  return Array.isArray(result) ? result : [result];
};

const ConfigurationFields = ({
  selectedDestinationId,
  configSchema,
}: ConfigSchemaProps) => {
  const selectedConfig = configSchema.oneOf?.find(
    (config) => config.title === selectedDestinationId,
  );

  if (!selectedConfig) {
    return null;
  }

  const requiredFields = selectedConfig.required || [];
  const properties = selectedConfig.properties || {};

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

export const DestinationConfiguration = ({ endpointData }: { endpointData: OptionalEndpointData }) => {
  const [destinationConfigs] = useState<DestinationConfig[]>(destinationConfigsData);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedDestination, setSelectedDestination] = useState<DestinationConfig | null>(
    destinationConfigsData.length > 0 ? destinationConfigsData[0] : null,
  );

  const filteredDestinations = useMemo(() => {
    if (!searchQuery.trim()) {
      return destinationConfigs;
    }
    const query = searchQuery.toLowerCase();
    return destinationConfigs.filter(
      (destination) =>
        destination.displayName.toLowerCase().includes(query) ||
        destination.id.toLowerCase().includes(query),
    );
  }, [searchQuery, destinationConfigs]);

  const handleDestinationSelect = (destination: DestinationConfig) => {
    setSelectedDestination(destination);
  };

  const configurationSchema = {
    oneOf: destinationConfigs.map(config => ({
      ...config.schema,
      title: config.id,
    }))
  };

  return (
    <>
      {destinationConfigs.length > 0 && (
        <>
          <Combobox
            immediate
            value={selectedDestination}
            onChange={handleDestinationSelect}
            onClose={() => setSearchQuery("")}
          >
            <div className={styles.comboboxWrapper}>
              <ComboboxInput
                id="destination-combobox"
                className={styles.input}
                placeholder="Search destinations..."
                displayValue={(destination: DestinationConfig | null) => destination?.id ?? ""}
                onChange={(event: React.ChangeEvent<HTMLInputElement>) => setSearchQuery(event.target.value)}
                autoComplete="off"
              />
              <ComboboxButton className={styles.dropdownButton}>
                <FontAwesomeIcon icon={faChevronDown} />
              </ComboboxButton>
            </div>

            <ComboboxOptions className={styles.dropdown} anchor="bottom">
              {filteredDestinations.length === 0 ? (
                <div className={styles.noResults}>
                  {searchQuery
                    ? `No destinations found for "${searchQuery}"`
                    : "No destinations available"}
                </div>
              ) : (
                filteredDestinations.map((destination) => (
                  <ComboboxOption
                    key={destination.id}
                    value={destination}
                    className={({ active, selected }: { active: boolean; selected: boolean }) =>
                      `${styles.option} ${active ? styles.active : ""} ${
                        selected ? styles.selected : ""
                      }`
                    }
                  >
                    <span className={styles.optionId}>{destination.id}</span>
                  </ComboboxOption>
                ))
              )}
            </ComboboxOptions>
          </Combobox>

          {selectedDestination && configurationSchema.oneOf && (
            <ConfigurationFields
              selectedDestinationId={selectedDestination.id}
              configSchema={configurationSchema}
            />
          )}
        </>
      )}
    </>
  );
};
