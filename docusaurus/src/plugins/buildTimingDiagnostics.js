/**
 * Docusaurus plugin for diagnosing build timing issues.
 * Logs timestamps at each lifecycle hook to identify bottlenecks.
 * 
 * This helps identify where time is spent during the Docusaurus build:
 * - loadContent: Plugins load their content (docs, blog posts, etc.)
 * - contentLoaded: Content is processed and routes are created
 * - configureWebpack: Webpack configuration is set up
 * - postBuild: After static site generation completes (before llms.txt runs)
 */

const logWithTimestamp = (phase, message) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] [build-timing] [${phase}] ${message}`);
};

// Track global build start time
let globalBuildStart = null;

module.exports = function buildTimingDiagnosticsPlugin(context, options) {
  if (!globalBuildStart) {
    globalBuildStart = Date.now();
  }
  const pluginStartTime = Date.now();
  let phaseTimings = {};
  
  const recordPhase = (phase) => {
    const now = Date.now();
    const sincePluginInit = now - pluginStartTime;
    const sinceBuildStart = now - globalBuildStart;
    phaseTimings[phase] = { timestamp: now, sincePluginInit, sinceBuildStart };
    logWithTimestamp(phase, `Started (${sincePluginInit}ms since plugin init, ${sinceBuildStart}ms since build start)`);
  };

  logWithTimestamp('init', `Plugin initialized (build started ${Date.now() - globalBuildStart}ms ago)`);

  return {
    name: 'build-timing-diagnostics',

    async loadContent() {
      recordPhase('loadContent');
      logWithTimestamp('loadContent', 'Starting to load content from all doc plugins...');
      // Return empty content - this plugin doesn't load any content
      return null;
    },

    async contentLoaded({ content, actions }) {
      recordPhase('contentLoaded');
      logWithTimestamp('contentLoaded', 'All plugins have loaded their content. Routes are being created...');
    },

    configureWebpack(config, isServer, utils) {
      const phase = `configureWebpack-${isServer ? 'server' : 'client'}`;
      recordPhase(phase);
      logWithTimestamp(phase, `Webpack ${isServer ? 'server' : 'client'} bundle configuration starting...`);
      // Don't modify webpack config, just log
      return {};
    },

    // This runs BEFORE static site generation
    async allContentLoaded({ content, actions }) {
      recordPhase('allContentLoaded');
      logWithTimestamp('allContentLoaded', 'All content loaded. Static site generation will begin soon...');
    },

    async postBuild(props) {
      recordPhase('postBuild');
      const totalTime = Date.now() - globalBuildStart;
      logWithTimestamp('postBuild', `Static site generation complete! Total build time: ${totalTime}ms (${(totalTime/1000/60).toFixed(2)} minutes)`);
      logWithTimestamp('postBuild', 'llms.txt plugin will run next (if enabled)...');
      
      // Log summary of all phases
      console.log('\n[build-timing] === BUILD PHASE TIMING SUMMARY ===');
      const phases = Object.entries(phaseTimings);
      for (let i = 0; i < phases.length; i++) {
        const [phase, data] = phases[i];
        const previousTimestamp = i > 0 ? phases[i-1][1].timestamp : globalBuildStart;
        const phaseDuration = data.timestamp - previousTimestamp;
        const minutes = (phaseDuration / 1000 / 60).toFixed(2);
        console.log(`[build-timing] ${phase}: +${phaseDuration}ms (${minutes} min) | Total: ${data.sinceBuildStart}ms`);
      }
      console.log('[build-timing] === END SUMMARY ===\n');
    },
  };
};
