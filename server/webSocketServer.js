const { WebSocketServer } = require('ws');
const handleAction = require('../actions');
const config = require('../utils/config');

/**
 * 等待bot.entity可用后再发送初始状态
 * @param {Bot} bot - mineflayer机器人实例
 */
function sendInitialStateWhenReady(ws, bot) {
    const checkInterval = setInterval(() => {
        if (bot && bot.entity) {
            clearInterval(checkInterval);
            console.log("机器人实体已确认，发送初始状态。");
            sendState(ws, bot);
        } else {
            console.log("正在等待机器人实体生成...");
        }
    }, 500);
    setTimeout(() => {
        clearInterval(checkInterval);
    }, 10000);
}


function startWebSocketServer(bot) {
  const wss = new WebSocketServer({ port: config.server.ws_port });
  console.log(`WebSocket 服务器已在端口 ${config.server.ws_port} 上启动。`);

  wss.on('connection', ws => {
    console.log('Python AI 代理已连接。');
    sendInitialStateWhenReady(ws, bot);

    ws.on('message', async message => {
      const data = JSON.parse(message);
      if (data.type === 'action' && bot && bot.entity) {
        try {
            const pos = bot.entity.position;
            console.log(`[坐标] X: ${pos.x.toFixed(2)}, Y: ${pos.y.toFixed(2)}, Z: ${pos.z.toFixed(2)}`);
            await handleAction(bot, data.action);
        } catch (error) {
            console.error("处理动作时发生错误:", error);
        } finally {
            sendState(ws, bot);
        }
      }
    });

    ws.on('close', () => console.log('Python AI 代理已断开连接。'));
  });
}

function sendState(client, bot) {
    if (!client || client.readyState !== client.OPEN || !bot || !bot.entity) {
        console.warn("尝试发送状态失败: WebSocket 未打开或 bot 实体不存在。");
        return;
    }
  
    const statePayload = {
      basic: {
        health: bot.health,
        food: bot.food,
        position: bot.entity.position,
        yaw: bot.entity.yaw,
        pitch: bot.entity.pitch,
        onGround: bot.entity.onGround,
      },
    };
    try {
        const message = JSON.stringify(statePayload);
        client.send(message);
        console.log("已发送当前状态至 Python。");
    }
    catch (error) {
        console.error("无法序列化或发送状态，可能包含无效值(NaN/Infinity):", error);
        console.error("状态内容:", statePayload);
    }
}

module.exports = { startWebSocketServer };