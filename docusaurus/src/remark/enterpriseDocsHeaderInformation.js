const { isEnterpriseConnectorDocsPage } = require("./utils");
const { toAttributes } = require("../helpers/objects");
const visit = require("unist-util-visit").visit;
const { catalog } = require("../connector_registry");

const getEnterpriseConnectorVersion = async (connectorType, connectorName) => {
  try {
    console.log(`[Enterprise Connector Debug] Starting version lookup for ${connectorType}/${connectorName}`);
    
    if (connectorName === "sap-hana") {
      console.log(`[Enterprise Connector Debug] Special case for SAP HANA`);
      
      const registry = await catalog;
      
      const sapHanaEnterprise = registry.find(
        (r) => r.dockerRepository_oss === "airbyte/source-sap-hana-enterprise"
      );
      
      if (sapHanaEnterprise && sapHanaEnterprise.dockerImageTag_oss) {
        console.log(`[Enterprise Connector Debug] Found SAP HANA enterprise connector:`, {
          name: sapHanaEnterprise.name_oss || sapHanaEnterprise.name_cloud,
          dockerRepo: sapHanaEnterprise.dockerRepository_oss,
          version: sapHanaEnterprise.dockerImageTag_oss
        });
        
        if (typeof window !== 'undefined') {
          console.log(`[Client] Found SAP HANA enterprise connector with version: ${sapHanaEnterprise.dockerImageTag_oss}`);
        }
        
        return sapHanaEnterprise.dockerImageTag_oss;
      }
    }
    
    const originalConnectorName = connectorName;
    if (connectorName === "sap-hana") {
      console.log(`[Enterprise Connector Debug] Trying alternate name for SAP HANA, checking source-volcano`);
      connectorName = "volcano";
    }
    
    const registry = await catalog;
    console.log(`[Enterprise Connector Debug] Registry loaded with ${registry.length} entries`);
    
    const enterpriseRepoPatterns = [
      `airbyte/source-${originalConnectorName}-enterprise`,
      `airbyte/destination-${originalConnectorName}-enterprise`
    ];
    
    console.log(`[Enterprise Connector Debug] Checking enterprise-specific patterns:`, enterpriseRepoPatterns);
    
    for (const repoName of enterpriseRepoPatterns) {
      console.log(`[Enterprise Connector Debug] Trying enterprise pattern: ${repoName}`);
      
      const registryEntry = registry.find(
        (r) => r.dockerRepository_oss === repoName
      );
      
      if (registryEntry) {
        console.log(`[Enterprise Connector Debug] Found enterprise entry for ${repoName}:`, {
          name: registryEntry.name_oss || registryEntry.name_cloud,
          dockerRepo: registryEntry.dockerRepository_oss,
          version: registryEntry.dockerImageTag_oss
        });
        
        if (registryEntry.dockerImageTag_oss) {
          if (typeof window !== 'undefined') {
            console.log(`[Client] Found enterprise connector with version: ${registryEntry.dockerImageTag_oss}`);
          }
          
          return registryEntry.dockerImageTag_oss;
        }
      }
    }
    
    const sapConnectors = registry.filter(
      (r) => (r.name_oss && r.name_oss.toLowerCase().includes("sap")) || 
             (r.name_cloud && r.name_cloud.toLowerCase().includes("sap")) ||
             (r.name_oss && r.name_oss.toLowerCase().includes("hana")) || 
             (r.name_cloud && r.name_cloud.toLowerCase().includes("hana"))
    );
    
    console.log(`[Enterprise Connector Debug] Found ${sapConnectors.length} SAP-related connectors:`, 
      sapConnectors.map(c => ({
        name: c.name_oss || c.name_cloud,
        dockerRepo: c.dockerRepository_oss,
        version: c.dockerImageTag_oss
      }))
    );
    
    const volcanoConnectors = registry.filter(
      (r) => (r.name_oss && r.name_oss.toLowerCase().includes("volcano")) || 
             (r.name_cloud && r.name_cloud.toLowerCase().includes("volcano")) ||
             (r.dockerRepository_oss && r.dockerRepository_oss.toLowerCase().includes("volcano"))
    );
    
    console.log(`[Enterprise Connector Debug] Found ${volcanoConnectors.length} volcano-related connectors:`, 
      volcanoConnectors.map(c => ({
        name: c.name_oss || c.name_cloud,
        dockerRepo: c.dockerRepository_oss,
        version: c.dockerImageTag_oss
      }))
    );
    
    console.log(`[Enterprise Connector Debug] Strategy 1: Direct match by name`);
    const directMatch = registry.find(
      (r) => (r.name_oss && r.name_oss.toLowerCase() === `sap ${originalConnectorName}`) || 
             (r.name_cloud && r.name_cloud.toLowerCase() === `sap ${originalConnectorName}`) ||
             (r.name_oss && r.name_oss.toLowerCase() === originalConnectorName) || 
             (r.name_cloud && r.name_cloud.toLowerCase() === originalConnectorName)
    );
    
    if (directMatch && directMatch.dockerImageTag_oss) {
      console.log(`[Enterprise Connector Debug] Found direct match:`, {
        name: directMatch.name_oss || directMatch.name_cloud,
        dockerRepo: directMatch.dockerRepository_oss,
        version: directMatch.dockerImageTag_oss
      });
      return directMatch.dockerImageTag_oss;
    }
    
    console.log(`[Enterprise Connector Debug] Strategy 2: Search by name pattern`);
    const namePatterns = [
      new RegExp(`${connectorName}`, 'i'),
      new RegExp(`${originalConnectorName}`, 'i'),
      new RegExp(`sap.*${originalConnectorName.replace('-', '\\s+')}`, 'i')
    ];
    
    for (const pattern of namePatterns) {
      console.log(`[Enterprise Connector Debug] Trying name pattern: ${pattern}`);
      
      const connectorsByName = registry.filter(
        (r) => (r.name_oss && r.name_oss.match(pattern)) || 
               (r.name_cloud && r.name_cloud.match(pattern))
      );
      
      console.log(`[Enterprise Connector Debug] Found ${connectorsByName.length} connectors matching pattern ${pattern}`);
      
      if (connectorsByName.length > 0) {
        console.log(`[Enterprise Connector Debug] Connectors found by name:`, 
          connectorsByName.map(c => ({
            name: c.name_oss || c.name_cloud,
            dockerRepo: c.dockerRepository_oss,
            version: c.dockerImageTag_oss
          }))
        );
        
        const connectorWithVersion = connectorsByName.find(c => c.dockerImageTag_oss);
        if (connectorWithVersion && connectorWithVersion.dockerImageTag_oss) {
          console.log(`[Enterprise Connector Debug] Using version from name match: ${connectorWithVersion.dockerImageTag_oss}`);
          return connectorWithVersion.dockerImageTag_oss;
        }
      }
    }
    
    console.log(`[Enterprise Connector Debug] Strategy 3: Search by repository patterns`);
    const possibleRepoNames = [
      `airbyte/${connectorType.replace(/s$/, "")}-${connectorName}`,
      `airbyte/source-${connectorName}`,
      `airbyte/destination-${connectorName}`,
      `airbyte/${connectorName}`,
      `${connectorName}`,
      `airbyte/${connectorType.replace(/s$/, "")}-${originalConnectorName}`,
      `airbyte/source-${originalConnectorName}`,
      `airbyte/destination-${originalConnectorName}`,
      `airbyte/${originalConnectorName}`,
      `${originalConnectorName}`
    ];
    
    console.log(`[Enterprise Connector Debug] Trying repository patterns:`, possibleRepoNames);
    
    for (const repoName of possibleRepoNames) {
      console.log(`[Enterprise Connector Debug] Trying repository pattern: ${repoName}`);
      
      const registryEntry = registry.find(
        (r) => r.dockerRepository_oss === repoName
      );
      
      if (registryEntry) {
        console.log(`[Enterprise Connector Debug] Found entry for ${repoName}:`, {
          name: registryEntry.name_oss || registryEntry.name_cloud,
          dockerRepo: registryEntry.dockerRepository_oss,
          version: registryEntry.dockerImageTag_oss
        });
        
        if (registryEntry.dockerImageTag_oss) {
          return registryEntry.dockerImageTag_oss;
        }
      }
    }
    
    console.log(`[Enterprise Connector Debug] Strategy 4: Search for repository containing name`);
    const repoPatterns = [
      new RegExp(`${connectorName}`, 'i'),
      new RegExp(`${originalConnectorName}`, 'i')
    ];
    
    for (const pattern of repoPatterns) {
      console.log(`[Enterprise Connector Debug] Trying repo pattern: ${pattern}`);
      
      const connectorsByRepo = registry.filter(
        (r) => r.dockerRepository_oss && r.dockerRepository_oss.match(pattern)
      );
      
      console.log(`[Enterprise Connector Debug] Found ${connectorsByRepo.length} connectors with repo matching pattern ${pattern}`);
      
      if (connectorsByRepo.length > 0) {
        console.log(`[Enterprise Connector Debug] Connectors found by repo:`, 
          connectorsByRepo.map(c => ({
            name: c.name_oss || c.name_cloud,
            dockerRepo: c.dockerRepository_oss,
            version: c.dockerImageTag_oss
          }))
        );
        
        const connectorWithVersion = connectorsByRepo.find(c => c.dockerImageTag_oss);
        if (connectorWithVersion && connectorWithVersion.dockerImageTag_oss) {
          console.log(`[Enterprise Connector Debug] Using version from repo match: ${connectorWithVersion.dockerImageTag_oss}`);
          return connectorWithVersion.dockerImageTag_oss;
        }
      }
    }
    
    console.log(`[Enterprise Connector Debug] No version found for any repository pattern`);
  } catch (error) {
    console.warn(`[Enterprise Connector Debug] Error fetching version:`, error);
  }
  
  console.log(`[Enterprise Connector Debug] Falling back to "Unable to determine connector version"`);
  return "Unable to determine connector version"; // More informative fallback message
};

const plugin = () => {
  const transformer = async (ast, vfile) => {
    const isDocsPage = isEnterpriseConnectorDocsPage(vfile);
    if (!isDocsPage) return;

    const pathParts = vfile.path.split("/");
    let connectorType = "";
    let connectorName = "";
    
    for (let i = 0; i < pathParts.length; i++) {
      if (pathParts[i] === "enterprise-connectors" && i > 0) {
        if (i + 1 < pathParts.length) {
          const fileName = pathParts[i + 1];
          if (fileName.startsWith("source-")) {
            connectorType = "sources";
            connectorName = fileName.replace("source-", "").split(".")[0];
          } else if (fileName.startsWith("destination-")) {
            connectorType = "destinations";
            connectorName = fileName.replace("destination-", "").split(".")[0];
          }
          break;
        }
      }
    }
    
    console.log(`[Enterprise Transformer Debug] Processing file: ${vfile.path}`);
    console.log(`[Enterprise Transformer Debug] Connector type: ${connectorType}, name: ${connectorName}`);
    
    const version = await getEnterpriseConnectorVersion(connectorType, connectorName);
    console.log(`[Enterprise Transformer Debug] Version returned: ${version}`);
    
    if (typeof window !== 'undefined') {
      console.log(`[Client] Enterprise connector transformer processing ${connectorName} with version: ${version}`);
    }

    let firstHeading = true;

    visit(ast, "heading", (node) => {
      if (firstHeading && node.depth === 1 && node.children.length === 1) {
        const originalTitle = node.children[0].value;
        const originalId = node.data.hProperties.id;
        
        console.log(`[Enterprise Transformer Debug] Creating attributes for HeaderDecoration`);
        
        const attrDict = {
          isOss: false,
          isCloud: false,
          isPypiPublished: false,
          isEnterprise: true,
          supportLevel: "certified",
          dockerImageTag: version,
          github_url: undefined,
          originalTitle,
          originalId,
          // cdkVersion: version,
          // isLatestCDKString: boolToBoolString(isLatest),
          // cdkVersionUrl: url,
          // syncSuccessRate,
          // usageRate,
          // lastUpdated,
        };
        
        console.log(`[Enterprise Transformer Debug] Attributes created:`, attrDict);

        firstHeading = false;
        node.children = [];
        node.type = "mdxJsxFlowElement";
        node.name = "HeaderDecoration";
        node.attributes = toAttributes(attrDict);
      }
    });
  };
  return transformer;
};

module.exports = plugin;
