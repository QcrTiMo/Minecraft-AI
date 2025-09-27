const mcServer  = require('flying-squid');
const { MC_SERVER_PORT, MC_SERVER_VERSION } = require('../config');

function startMinecraftServer() {
  console.log("正在启动内存 Minecraft 服务器...");
  mcServer.createMCServer({
    'motd': 'A Server for AI Agents',
    'port': MC_SERVER_PORT,
    'max-players': 3,
    'gameMode': 1,
    'difficulty': 1,
    'worldFolder': 'training_background',
    'generation': {
      'name': 'superflat',
      'options': {
        'worldHeight': 80
      }
    },
    'modpe': false,
    'view-distance': 50,
    'online-mode': false,
    'plugins': {},
    'player-list-text': {
      'header': { "text": "AI Minecraft 代理" },
      'footer': { "text": "由 mineflayer 和 flying-squid 提供支持" }
    },
    'everybody-op': true,
    'max-entities': 100,
    'version': MC_SERVER_VERSION,
  });
  console.log(`Minecraft 服务器已在端口 ${MC_SERVER_PORT} 上启动。`);


}

module.exports = { startMinecraftServer };