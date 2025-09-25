const mineflayer = require('mineflayer');
const { WebSocketServer } = require('ws');
const { createMCServer } = require('flying-squid');
const { mineflayer: viewer } = require('prismarine-viewer');
const path = require('path');
const handleAction = require('./actions');
const { Bot } = require('./bot.js');


const MC_SERVER_PORT = 25565;
const MC_SERVER_VERSION = '1.21';
const WEB_SOCKET_PORT = 3000;
const VIEWER_PORT = 8080;

let bot = null;

function loadWorldGenerator() {
  //从命令行参数获取世界名称
  const worldName = process.argv[2] || 'flat_world';
  const generatorPath = path.join(__dirname, 'training_background', `${worldName}.js`);
  
  try {
    console.log(`尝试加载世界生成脚本: ${worldName}...`);
    return require(generatorPath);
  } catch (e) {
    console.error(`错误: 找不到名为 '${worldName}' 的世界生成脚本。`);
    console.error(`请确保文件 'mc-ai/training_background/${worldName}.js' 存在。`);
    process.exit(1); //找不到脚本则退出程序
  }
}

//在代码中创建一个Minecraft服务器
function startWebSocketServer(bot) {
  const wss = new WebSocketServer({ port: WEB_SOCKET_PORT });
  console.log(`WebSocket 服务器已在端口 ${WEB_SOCKET_PORT} 上启动。`);

  wss.on('connection', ws => {
    console.log('Python AI 代理已连接。');
    
    ws.on('message', async message => {
      const data = JSON.parse(message);
      if (data.type === 'action' && bot && bot.entity) {
        await handleAction(bot, data.action);
        sendState(ws, bot);
      }
    });

    ws.on('close', () => console.log('Python AI 代理已断开连接。'));

    if (bot && bot.entity) {
      sendState(ws, bot);
    }
  });
}

//启动浏览器可视化界面
function startViewer() {
  if (!bot) return;
  viewer(bot, { port: VIEWER_PORT });
  console.log(`可视化界面已启动，请在浏览器打开 http://localhost:${VIEWER_PORT}`);
}

//向指定的Python客户端发送状态
function sendState(client, bot) {
  if (!client || !bot || !bot.entity) return;

  const statePayload = {
    type: 'state',
    basic: {
      health: bot.health,
      food: bot.food,
      position: bot.entity.position,
      yaw: bot.entity.yaw,
      pitch: bot.entity.pitch,
    },
    surroundings: getSurroundingBlocks()
  };
  client.send(JSON.stringify(statePayload));
}

//按正确顺序启动所有服务
async function main() {
  //启动服务器
  await startMinecraftServer();
  //创建机器人实例
  console.log("正在创建并连接机器人...");
  const bot = await Bot({
    host: 'localhost',
    port: MC_SERVER_PORT,
    username: 'AI_Bot',
    version: MC_SERVER_VERSION,
    viewerPort: VIEWER_PORT
  });
  console.log(`可视化界面已启动，请在浏览器打开 http://localhost:${VIEWWER_PORT}`);
  startWebSocketServer(bot);
}

main();