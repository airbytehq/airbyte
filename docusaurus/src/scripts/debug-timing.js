#!/usr/bin/env node

/**
 * Debug timing script to track build progress
 * Logs timestamps at each stage of the build process
 */

const fs = require('fs');
const path = require('path');

const LOG_FILE = path.join(__dirname, '../../build-timing.log');

function log(stage, message = '') {
  const timestamp = new Date().toISOString();
  const timestamp_ms = Date.now();
  const entry = `[${timestamp}] ${stage}: ${message}\n`;

  console.log(entry.trim());
  fs.appendFileSync(LOG_FILE, entry);
}

function clearLog() {
  fs.writeFileSync(LOG_FILE, `Build timing log started: ${new Date().toISOString()}\n\n`);
}

// Export for use in other scripts
module.exports = { log, clearLog };

// If run directly
if (require.main === module) {
  const args = process.argv.slice(2);
  const stage = args[0] || 'UNKNOWN';
  const message = args.slice(1).join(' ');

  clearLog();
  log(stage, message);
}
