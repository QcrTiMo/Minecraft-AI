const { mineflayer: viewer } = require('prismarine-viewer');
const { VIEWER_PORT } = require('../config');

function startViewer(bot) {
  if (!bot) return;
  viewer(bot, { port: VIEWER_PORT });
  console.log(`可视化界面已启动，请在浏览器打开 http://localhost:${VIEWER_PORT}`);
}

module.exports = { startViewer };