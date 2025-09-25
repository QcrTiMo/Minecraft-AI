async function look(bot, { yaw, pitch }) {
    await bot.look(yaw, pitch);
    console.log(`动作: [视角] 已看至 yaw=${yaw.toFixed(2)}, pitch=${pitch.toFixed(2)}`);
}

async function move(bot, { direction, duration = 1000 }) {
    const ticksToWait = Math.round(duration / 50);
    
    if (ticksToWait < 1) {
        console.warn(`警告: 移动时长 ${duration}ms 太短，无法转换为有效的游戏刻。`);
        return;
    }

    console.log(`动作: [移动] 开始朝 ${direction} 方向移动，持续 ${ticksToWait} 个游戏刻...`);
    bot.setControlState(direction, true);
    await bot.waitForTicks(ticksToWait);
    bot.setControlState(direction, false);

    console.log(`动作: [移动] 已停止朝 ${direction} 方向移动。`);
}

async function jump(bot) {
    console.log('动作: [跳跃] 执行跳跃');
    bot.setControlState('jump', true);
    bot.setControlState('jump', false);
}

async function turn(bot, { angle_change }) {
    //angle_change是一个以弧度为单位的增量
    const currentYaw = bot.entity.yaw;
    const newYaw = currentYaw + angle_change;
    await bot.look(newYaw, bot.entity.pitch, true); //第三个参数true表示强制看向
    console.log(`动作: [视角] 转向 ${angle_change.toFixed(2)} 弧度`);
}

module.exports = {
    look,
    move,
    jump,
    turn,
    //TODO
};