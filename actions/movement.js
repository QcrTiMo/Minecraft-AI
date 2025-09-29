/**
 * 辅助函数：将一个需要持续时间的动作封装成 Promise，确保执行时间
 * @param {function} start - 开始动作的函数
 * @param {function} stop - 停止动作的函数
 * @param {number} duration - 持续时间 (毫秒)
 */
function timedStateAction(start, stop, duration) {
    return new Promise((resolve) => {
    start();
    setTimeout(() => {

        stop();
        setTimeout(resolve, 50);
    }, duration);
    });
}

async function look(bot, { yaw, pitch }) {
    await bot.look(yaw, pitch, true);
    console.log(`动作: [视角] 已看至 yaw=${yaw.toFixed(2)}, pitch=${pitch.toFixed(2)}`);
}

async function move(bot, { direction, duration = 250 }) {
    if (direction === 'forward') {
        console.log(`动作: [移动] 开始向前疾跑，持续 ${duration}ms...`);
        try {
            bot.setControlState('forward', true);
            await new Promise(resolve => setTimeout(resolve, 50));
            bot.setControlState('sprint', true);
            await new Promise(resolve => setTimeout(resolve, duration));
        }
        finally {
            bot.setControlState('forward', false);
            bot.setControlState('sprint', false);
            console.log(`动作: [移动] 已停止向前疾跑。`);
        }
        await new Promise(resolve => setTimeout(resolve, 50));

    } 
    else {
        console.log(`动作: [移动] 开始朝 ${direction} 方向移动，持续 ${duration}ms...`);
        await timedStateAction(
            () => bot.setControlState(direction, true),
            () => bot.setControlState(direction, false),
            duration
        );
        console.log(`动作: [移动] 已停止朝 ${direction} 方向移动。`);
    }
}


async function jump(bot) {
    console.log('动作: [跳跃] 执行跳跃');
    bot.setControlState('jump', true);
    bot.setControlState('jump', false);
    await new Promise(resolve => setTimeout(resolve, 150));
}

async function turn(bot, { angle_change }) {
    const currentYaw = bot.entity.yaw;
    const newYaw = currentYaw + angle_change;
    await bot.look(newYaw, bot.entity.pitch, true);
    console.log(`动作: [视角] 转向 ${angle_change.toFixed(2)} 弧度`);
}

module.exports = {
    look,
    move,
    jump,
    turn,
};