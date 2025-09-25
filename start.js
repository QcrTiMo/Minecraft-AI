const { Bot } = require('./bot.js');
const { startMinecraftServer } = require('./server/mcServer');
const { startWebSocketServer } = require('./server/webSocketServer');
const { startViewer } = require('./viewer/viewer');

async function main() {
  //启动服务器
  await startMinecraftServer();
  //创建并连接机器人
  console.log("正在创建并连接机器人...");
  const bot = await Bot();
  //启动可视化界面
  startViewer(bot);
  //启动 WebSocket 服务器
  startWebSocketServer(bot);
}
main();