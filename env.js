const mineflayer = require('mineflayer');
const {WebSocketServer} = require('ws');


const BOT_OPTIONS = {
    host: 'localhost',
    port: 25565,
    username: 'AI_Bot',
    version: '1.21'
};
const WEB_SOCKET_PORT = 3000;

let bot = null;
let wss = null;
let pythonClient = null;

function startBot() {
  bot = mineflayer.createBot(BOT_OPTIONS);

  bot.on('login', () => {
    console.log('登录成功');
    bot.chat('我是QcrTiMo的AI机器人');
  });

  bot.on('kicked', (reason) => {
    console.log('Bot was kicked:', reason);
    bot = null;
  });

  bot.on('error', (err) => {
    console.log('Bot encountered an error:', err);
    bot = null;
  });


}

function startWebSocketServer() {
  wss = new WebSocketServer({ port: WEB_SOCKET_PORT });
  console.log(`WebSocket server started on port ${WEB_SOCKET_PORT}`);

  wss.on('connection', ws => {
    console.log('Python AI Agent connected.');
    pythonClient = ws;
    ws.on('message', message => {
      const data = JSON.parse(message);
      if (data.type === 'action') {
        handleAction(data.action);
      }
    });
    ws.on('close', () => {
      console.log('Python AI Agent disconnected.');
      pythonClient = null;
    });
    setInterval(() => {
        if (pythonClient && bot) {
            sendState();
        }
    }, 100);
  });
}
function handleAction(action) {
    if (!bot) return;
    switch(action.name) {
        case 'move_forward':
            bot.setControlState('forward', true);
            setTimeout(() => bot.setControlState('forward', false), 500); // 移动一小段时间
            break;
        case 'move_backward':
            bot.setControlState('back', true);
            setTimeout(() => bot.setControlState('back', false), 500);
            break;
        case 'jump':
            bot.setControlState('jump', true);
            bot.setControlState('jump', false);
        case 'chat':
            if (action.message) {
                bot.chat(action.message);
            }
            break;
    }
}
function sendState() {
    if (!pythonClient || !bot || !bot.entity) return;

    const state = {
        type: 'state',
        health: bot.health,
        food: bot.food,
        position: bot.entity.position,
    };

    pythonClient.send(JSON.stringify(state));
}


startBot();
startWebSocketServer();