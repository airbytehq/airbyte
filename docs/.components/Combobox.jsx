import React, { useState } from "react";
import { CheckIcon, ChevronUpDownIcon } from "@heroicons/react/20/solid";
import { Combobox } from "@headlessui/react";


function classNames(...classes) {
  return classes.filter(Boolean).join(" ");
}
export default function MyCombobox() {
  const [query, setQuery] = useState("");
  const [selectedConnector, setselectedConnector] = useState(null);

  const [connectors, setConnectors] = useState(null);
  React.useEffect(() => {
    fetch("https://airbyte-metadata.netlify.app/connectors")
      .then((res) => res.json())
      .then((data) => setConnectors(data));
  }, []);
  const filteredConnectors =
    query === ""
      ? connectors || []
      : connectors.filter((connector) => {
          return JSON.stringify(connector)
            .toLowerCase()
            .includes(query.toLowerCase());
        });

  return (
    <Combobox
      as="div"
      value={selectedConnector}
      onChange={(value) => {
        console.log({ value });
        if (value === "notfound") {
          window.location.href = "https://airbyte.com/connector-requests";
          setselectedConnector(null);
        } else {
          window.location.href = value.documentationUrl;
        }
        setselectedConnector(value);
      }}
    >
      <Combobox.Label className="block">
        Quick navigate to Connector docs (full search + filters <a href="https://docs.airbyte.com/integrations/">here</a>):
      </Combobox.Label>
      <div className="relative mt-1">
        <Combobox.Input
          className="w-full py-2 pl-3 pr-10 text-black bg-white border border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 sm:text-sm"
          onChange={(event) => setQuery(event.target.value)}
          displayValue={(person) => person?.name}
          placeholder="Search for a connector"
        />
        <Combobox.Button className="absolute inset-y-0 right-0 flex items-center px-2 bg-indigo-800 border-none dark:shadow-sm dark:bg-indigo-200 rounded-r-md focus:outline-none">
          <ChevronUpDownIcon
            className="w-5 h-5 text-gray-400 dark:text-gray-900"
            aria-hidden="true"
          />
        </Combobox.Button>

        {filteredConnectors.length > 0 ? (
          <Combobox.Options className="absolute z-10 w-full py-1 pl-0 mt-1 overflow-auto text-base list-none bg-white rounded-md shadow-lg max-h-56 ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
            {filteredConnectors.map((connector) => (
              <Combobox.Option
                key={connector.name}
                value={connector}
                className={({ active }) =>
                  classNames(
                    "relative cursor-default select-none py-2 pl-3 pr-9",
                    active ? "bg-indigo-200 text-black" : "text-gray-900"
                  )
                }
              >
                {({ active, selected }) => (
                  <>
                    <div className="flex items-center">
                      {connector.iconUrl && (
                        <img
                          src={
                            // "https://raw.githubusercontent.com/airbytehq/airbyte/master/airbyte-config/init/src/main/resources/icons/" +
                            connector.iconUrl
                          }
                          alt=""
                          className="flex-shrink-0 w-12 h-12 bg-gray-200 rounded-full"
                        />
                      )}
                      <div className="flex flex-col ml-3">
                        <span
                          className={classNames(
                            "truncate",
                            selected && "font-semibold"
                          )}
                        >
                          {connector.displayName}
                        </span>
                        <span className="font-mono text-xs text-gray-600 truncate">
                          {connector.name}
                        </span>
                      </div>
                    </div>

                    {selected && (
                      <span
                        className={classNames(
                          "absolute inset-y-0 right-0 flex items-center pr-4",
                          active ? "text-white" : "text-indigo-600"
                        )}
                      >
                        <CheckIcon className="w-5 h-5" aria-hidden="true" />
                      </span>
                    )}
                  </>
                )}
              </Combobox.Option>
            ))}
            <Combobox.Option
              key={"notfound"}
              value={"notfound"}
              className={({ active }) =>
                classNames(
                  "relative cursor-default select-none py-2 pl-3 pr-9",
                  active ? "bg-indigo-200 text-white" : "text-gray-900"
                )
              }
            >
              {({ selected }) => (
                <>
                  <div className="flex items-center">
                    <span
                      className={classNames(
                        "ml-3 truncate",
                        selected && "font-semibold"
                      )}
                    >
                      Not found - request a connector!
                    </span>
                  </div>
                </>
              )}
            </Combobox.Option>
          </Combobox.Options>
        ) : (
          <Combobox.Options className="absolute z-10 w-full py-1 pl-0 mt-1 overflow-auto text-base list-none bg-white rounded-md shadow-lg max-h-56 ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
            <Combobox.Option
              key={"notfound"}
              value={"notfound"}
              className={({ active }) =>
                classNames(
                  "relative cursor-default select-none py-2 pl-3 pr-9",
                  active ? "bg-indigo-600 text-white" : "text-gray-900"
                )
              }
            >
              {({ selected }) => (
                <>
                  <div className="flex items-center">
                    <span
                      className={classNames(
                        "ml-3 truncate",
                        selected && "font-semibold"
                      )}
                    >
                      Not found - request a connector!
                    </span>
                  </div>
                </>
              )}
            </Combobox.Option>
          </Combobox.Options>
        )}
      </div>
    </Combobox>
  );
}
