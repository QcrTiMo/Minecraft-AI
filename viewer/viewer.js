const mineflayerViewer = require('prismarine-viewer').mineflayer
const { VIEWER_PORT } = require('../config');

function Viewer(bot) {
  if (!bot) return;
  mineflayerViewer(bot, { port: VIEWER_PORT, firstPerson: false });
  console.log(`可视化界面已启动，请在浏览器打开 http://localhost:${VIEWER_PORT}`);
}

module.exports = { Viewer };