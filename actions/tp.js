async function tp(bot, { x, y, z }) {
    const command = `/tp @s ${x} ${y} ${z}`;
    console.log(`动作: [传送] 执行命令: ${command}`);
    await bot.chat(command);
    await new Promise(resolve => setTimeout(resolve, 100));
}

async function resetPosition(bot) {
    const resetCoords = { x: 0, y: -60, z: 0 };
    const command = `/tp @s ${resetCoords.x} ${resetCoords.y} ${resetCoords.z}`;
    console.log(`动作: [重置位置] 回合结束，传送至初始点: ${command}`);
    await bot.chat(command);
    await new Promise(resolve => setTimeout(resolve, 100));
}

module.exports = {
    tp,
    resetPosition,
};