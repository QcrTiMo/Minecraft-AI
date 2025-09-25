const { WebSocketServer } = require('ws');
const handleAction = require('../actions');
const { WEB_SOCKET_PORT } = require('../config');

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
    };
    client.send(JSON.stringify(statePayload));
}

module.exports = { startWebSocketServer };