const { createMCServer } = require('flying-squid');
const { loadWorldGenerator } = require('../utils/worldLoader');
const { MC_SERVER_PORT, MC_SERVER_VERSION } = require('../config');

function startMinecraftServer() {
  console.log("正在启动内存 Minecraft 服务器...");
  const mcServer = createMCServer({
    'port': MC_SERVER_PORT,
    'version': MC_SERVER_VERSION,
    'online-mode': false,
    'world': loadWorldGenerator(),
    'plugins': {},
    'player-list-text': {
      'header': { "text": "AI Minecraft 代理" },
      'footer': { "text": "由 mineflayer 和 flying-squid 提供支持" }
    }
  });
  console.log(`Minecraft 服务器已在端口 ${MC_SERVER_PORT} 上启动。`);


}

module.exports = { startMinecraftServer };