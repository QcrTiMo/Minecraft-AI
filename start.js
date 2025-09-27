const { Bot } = require('./bot.js');
//const { startMinecraftServer } = require('./server/mcServer');
const { startWebSocketServer } = require('./server/webSocketServer');

async function main() {
    try{
        //await startMinecraftServer();
        console.log("正在创建并连接机器人...");
        const bot = await Bot();
        startWebSocketServer(bot);
    }
    catch(error){
        console.error("启动过程中发生致命错误:", error);
        process.exit(1);
    }
};
main().catch(error => {
    console.error("捕获到未处理的 Promise 拒绝:", error);
    process.exit(1);
});