/**
 * ChatWidget Theme Plugin for Docusaurus
 * Injects ChatWidget globally across all documentation pages
 */

const path = require('path');

module.exports = function () {
  return {
    name: 'chat-widget-plugin',
    
    // Inject Root wrapper component
    getThemePath() {
      return path.join(__dirname, 'ChatWidgetWrapper');
    },

    getClientModules() {
      return [];
    },
  };
};
