const mineflayerViewer = require('prismarine-viewer').mineflayer
const { VIEWER_PORT } = require('../config');

function Viewer(bot) {
  if (!bot) return;
  mineflayerViewer(bot, { port: VIEWER_PORT, firstPerson: false });
  
  const path = [bot.entity.position.clone()]
  bot.on('move', () => {
    if (path[path.length - 1].distanceTo(bot.entity.position) > 1) {
      path.push(bot.entity.position.clone())
      bot.viewer.drawLine('path', path)
    }
  })
  console.log(`可视化界面已启动，请在浏览器打开 http://localhost:${VIEWER_PORT}`);
}

module.exports = { Viewer };