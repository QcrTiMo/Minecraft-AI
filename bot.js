const mineflayer = require('mineflayer');
const { MC_SERVER_PORT, MC_SERVER_VERSION, VIEWER_PORT } = require('./config');

function Bot() {
  return new Promise((resolve, reject) => {
    const bot = mineflayer.createBot({
      host: 'localhost',
      port: MC_SERVER_PORT,
      username: 'AI_Bot',
      version: MC_SERVER_VERSION,
      viewerPort: VIEWER_PORT
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
      const path = [bot.entity.position.clone()];
      bot.chat(`/tp @s 0 61 0`);
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