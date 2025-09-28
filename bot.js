const mineflayer = require('mineflayer')
const config = require('./utils/config');

function Bot() {
  return new Promise((resolve, reject) => {
    const bot = mineflayer.createBot({
      host: config.server.host,
      port: config.server.mc_port,
      username: config.server.name,
    });

    bot.once('spawn', () => {
      console.log('机器人已成功在本地服务器中生成完毕。');
      resolve(bot);
    });

    bot.on('error', err => reject(err));
    bot.on('end', reason => console.log(`机器人断开连接: ${reason}`));
  });
}

module.exports = { Bot };