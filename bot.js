const mineflayer = require('mineflayer');
const { mineflayer: viewer } = require('prismarine-viewer');

function Bot(options) {
  return new Promise((resolve, reject) => {
    const bot = mineflayer.createBot({
      host: options.host,
      port: options.port,
      username: options.username,
      version: options.version,
    });

    bot.on('login', () => {
      console.log('机器人已成功登录到本地服务器。');
    });

    bot.on('error', (err) => {
      console.log('机器人遇到错误:', err);
      reject(err);
    });

    bot.once('spawn', () => {
      console.log('机器人在世界中生成完毕。');
      viewer(bot, { port: options.viewerPort });
      const path = [bot.entity.position.clone()];
      bot.on('move', () => {
        if (path[path.length - 1].distanceTo(bot.entity.position) > 1) {
          path.push(bot.entity.position.clone());
          bot.viewer.drawLine('path', path);
        }
      });
      resolve(bot);
    });
  });
}

module.exports = { Bot };