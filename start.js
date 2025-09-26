const { Bot } = require('./bot.js');
const { startMinecraftServer } = require('./server/mcServer');
const { startWebSocketServer } = require('./server/webSocketServer');

async function main() {
    await startMinecraftServer();
    console.log("正在创建并连接机器人...");
    const bot = await Bot();
    startWebSocketServer(bot);
};
main();