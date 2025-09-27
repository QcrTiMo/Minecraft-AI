const mineflayer = require('mineflayer')
const { MC_SERVER_PORT } = require('./config');
//const { Viewer } = require('./viewer/viewer');

function Bot() {
  return new Promise((resolve, reject) => {
    const bot = mineflayer.createBot({
      host: 'localhost',
      port: MC_SERVER_PORT,
      username: 'AI_Bot',
    });

    bot.once('spawn', () => {
      //Viewer(bot);
      console.log('机器人已成功在本地服务器中生成完毕。');
      resolve(bot);
    });

    bot.on('error', err => reject(err));
    bot.on('end', reason => console.log(`机器人断开连接: ${reason}`));
  });
}

module.exports = { Bot };