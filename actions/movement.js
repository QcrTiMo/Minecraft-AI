//异步函数，因为有些动作需要时间完成
async function look(bot, { yaw, pitch }) {
    //让机器人看向指定的方向（弧度制）
    await bot.look(yaw, pitch);
    console.log(`动作: 看向 yaw=${yaw}, pitch=${pitch}`);
}

async function move(bot, { direction, duration = 100 }) {
    //按下指定的方向键一段时间
    bot.setControlState(direction, true);
    await new Promise(resolve => setTimeout(resolve, duration));
    bot.setControlState(direction, false);
    console.log(`动作: 向 ${direction} 方向移动 ${duration}ms`);
}

async function jump(bot) {
    bot.setControlState('jump', true);
    bot.setControlState('jump', false);
    console.log('动作: 跳跃');
}

module.exports = {
    look,
    move,
    jump,
};