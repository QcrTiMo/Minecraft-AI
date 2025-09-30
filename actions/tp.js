async function tp(bot, { x, y, z }) {
    const command = `/tp @s ${x} ${y} ${z}`;
    console.log(`动作: [传送] 执行命令: ${command}`);
    await bot.chat(command);
    await new Promise(resolve => setTimeout(resolve, 100));
}

module.exports = {
    tp,
};