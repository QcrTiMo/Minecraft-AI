const mineflayer = require('mineflayer')
const { MC_SERVER_PORT, MC_SERVER_VERSION, VIEWER_PORT } = require('./config');
const { Viewer } = require('./viewer/viewer');

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
      Viewer(bot);
      console.log('机器人在世界中生成完毕。');
//      bot.chat(`/tp @s 0 61 0`);
      setTimeout(() => {
//        console.log(`传送完成，当前坐标: Y=${bot.entity.position.y.toFixed(2)}`);

        resolve(bot);
      }, 1000);
    });
  });
}

module.exports = { Bot };