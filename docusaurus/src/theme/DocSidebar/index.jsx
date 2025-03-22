import DocSidebar from "@theme-original/DocSidebar";
import { useEffect, useState } from "react";
import { REGISTRY_URL } from "../../connector_registry";
import { getConnectorsBySupportLevel } from "./utils";

async function fetchCatalog(url, setter) {
  const response = await fetch(url);
  const registry = await response.json();
  setter(registry);
}


export default function DocSidebarWrapper(props) {
 
  const [registry, setRegistry] = useState([]);
  const [sidebar, setSidebar] = useState(props.sidebar);
  useEffect(() => {
    fetchCatalog(REGISTRY_URL, setRegistry);
  }, []);
  
  useEffect(() => {
    if(registry.length === 0) return;
    const connectorCatalogItem = sidebar.find(item => item.label === "Connector Catalog")
    const sourcesItem = connectorCatalogItem.items.find(item => item.label === "Sources");
    const destinationsItem = connectorCatalogItem.items.find(item => item.label === "Destinations");
   
    
    const groupedSourcesItems = getConnectorsBySupportLevel(sourcesItem.items, registry);
    const groupedDestinationsItems = getConnectorsBySupportLevel(destinationsItem.items, registry);

  
    setSidebar((prev) => {
      const newSidebar = structuredClone(prev); 
      const connectorCatalogItem = newSidebar.find(item => item.label === "Connector Catalog");
      const sourcesItem = connectorCatalogItem.items.find(item => item.label === "Sources");
      sourcesItem.items = groupedSourcesItems;
      const destinationsItem = connectorCatalogItem.items.find(item => item.label === "Destinations");
      destinationsItem.items = groupedDestinationsItems;
      return newSidebar;
    });
  }, [registry]);

  return (
    <>
      <DocSidebar {...props} sidebar={sidebar} />
    </>
  );
}
