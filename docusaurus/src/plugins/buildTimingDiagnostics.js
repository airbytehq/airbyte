/**
 * Docusaurus plugin for diagnosing build timing issues.
 * Logs timestamps at each lifecycle hook to identify bottlenecks.
 * 
 * This helps identify where time is spent during the Docusaurus build:
 * - loadContent: Plugins load their content (docs, blog posts, etc.)
 * - contentLoaded: Content is processed and routes are created
 * - configureWebpack/Rspack: Bundler configuration is set up
 * - Rspack compiler hooks: Track bundling progress (using only Rspack-compatible hooks)
 * - postBuild: After static site generation completes (before llms.txt runs)
 */

const logWithTimestamp = (phase, message) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] [build-timing] [${phase}] ${message}`);
};

// Track global build start time
let globalBuildStart = null;

// Create a Rspack/Webpack plugin class for timing hooks
// NOTE: Only using compiler-level hooks that are compatible with Rspack
// Rspack's compilation object has different hooks than webpack
class BundlerTimingPlugin {
  constructor(recordPhase, isServer) {
    this.recordPhase = recordPhase;
    this.isServer = isServer;
    this.bundleType = isServer ? 'server' : 'client';
  }

  apply(compiler) {
    const bundleType = this.bundleType;
    const recordPhase = this.recordPhase;

    // Log when compilation starts (compiler-level hook, works with Rspack)
    compiler.hooks.beforeCompile.tap('BundlerTimingPlugin', () => {
      recordPhase(`rspack-beforeCompile-${bundleType}`);
      logWithTimestamp(`rspack-${bundleType}`, 'Rspack compilation starting...');
    });

    // Log when compilation object is created (compiler-level hook, works with Rspack)
    compiler.hooks.compilation.tap('BundlerTimingPlugin', (compilation) => {
      recordPhase(`rspack-compilation-${bundleType}`);
      logWithTimestamp(`rspack-${bundleType}`, 'Rspack compilation object created');
    });

    // Log when assets are about to be emitted (compiler-level hook, works with Rspack)
    compiler.hooks.emit.tapAsync('BundlerTimingPlugin', (compilation, callback) => {
      const assetCount = Object.keys(compilation.assets || {}).length;
      recordPhase(`rspack-emit-${bundleType}`);
      logWithTimestamp(`rspack-${bundleType}`, `Emitting ${assetCount} assets...`);
      callback();
    });

    // Log after assets are emitted (compiler-level hook, works with Rspack)
    compiler.hooks.afterEmit.tapAsync('BundlerTimingPlugin', (compilation, callback) => {
      recordPhase(`rspack-afterEmit-${bundleType}`);
      logWithTimestamp(`rspack-${bundleType}`, 'Assets emitted');
      callback();
    });

    // Log when compilation is done (compiler-level hook, works with Rspack)
    compiler.hooks.done.tap('BundlerTimingPlugin', (stats) => {
      recordPhase(`rspack-done-${bundleType}`);
      const time = stats.endTime - stats.startTime;
      logWithTimestamp(`rspack-${bundleType}`, `Rspack ${bundleType} bundle complete! (${time}ms, ${(time/1000/60).toFixed(2)} min)`);
      
      // Log any warnings or errors
      if (stats.hasWarnings && stats.hasWarnings()) {
        const warningCount = stats.compilation?.warnings?.length || 'unknown';
        logWithTimestamp(`rspack-${bundleType}`, `Warnings: ${warningCount}`);
      }
      if (stats.hasErrors && stats.hasErrors()) {
        const errorCount = stats.compilation?.errors?.length || 'unknown';
        logWithTimestamp(`rspack-${bundleType}`, `Errors: ${errorCount}`);
      }
    });
  }
}

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
    logWithTimestamp(phase, `(${sincePluginInit}ms since plugin init, ${sinceBuildStart}ms since build start)`);
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
      logWithTimestamp(phase, `Rspack ${isServer ? 'server' : 'client'} bundle configuration starting...`);
      
      // Add our timing plugin to track Rspack compilation phases
      return {
        plugins: [new BundlerTimingPlugin(recordPhase, isServer)],
      };
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
