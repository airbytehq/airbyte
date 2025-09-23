const visit = require("unist-util-visit").visit;

const plugin = (options = {}) => {
  const transformer = async (ast, vfile) => {
    const variables = options.variables || {};
    
    if (vfile.path && vfile.path.includes('test-simple')) {
      console.log('=== PROCESSING TEST FILE ===');
      console.log('File path:', vfile.path);
      console.log('Variables available:', Object.keys(variables));
      console.log('AST root children count:', ast.children ? ast.children.length : 0);
    }
    
    visit(ast, (node) => {
      if (node.value && typeof node.value === "string" && node.value.includes("{{")) {
        console.log(`Found node with {{: type=${node.type}, value="${node.value}"`);
        
        const originalValue = node.value;
        node.value = node.value.replace(/\{\{(\w+)\}\}/g, (match, variableName) => {
          if (variables.hasOwnProperty(variableName)) {
            console.log(`Replacing ${match} with ${variables[variableName]}`);
            return variables[variableName];
          }
          return match;
        });
        
        if (originalValue !== node.value) {
          console.log(`Node value changed from "${originalValue}" to "${node.value}"`);
        }
      }
    });
  };
  return transformer;
};

module.exports = plugin;
