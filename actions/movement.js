async function move(bot, { direction, duration = 250 } = {}) {
    const canSprint = direction === 'forward' && bot.food > 6;

    if (canSprint) {
        console.log(`动作: [移动] 满足疾跑条件，开始向前疾跑，持续 ${duration}ms...`);
        bot.setControlState('forward', true);
        bot.setControlState('sprint', true);
    } else {
        console.log(`动作: [移动] 开始朝 ${direction} 方向移动，持续 ${duration}ms...`);
        bot.setControlState(direction, true);
    }

    await new Promise(resolve => setTimeout(resolve, duration));

    if (canSprint) {
        bot.setControlState('sprint', false);
    }
    bot.setControlState(direction, false);

    console.log(`动作: [移动] 已停止移动。`);
    await new Promise(resolve => setTimeout(resolve, 50));
}

async function jump(bot) {
    console.log('动作: [跳跃] 执行跳跃');
    bot.setControlState('jump', true);
    bot.setControlState('jump', false);
    await new Promise(resolve => setTimeout(resolve, 150));
}

async function look(bot, { yaw, pitch }) {
    await bot.look(yaw, pitch, true);
    console.log(`动作: [视角] 已看至 yaw=${yaw.toFixed(2)}, pitch=${pitch.toFixed(2)}`);
}

async function turn(bot, { angle_change }) {
    const currentYaw = bot.entity.yaw;
    const newYaw = currentYaw + angle_change;
    await bot.look(newYaw, bot.entity.pitch, true);
    console.log(`动作: [视角] 转向 ${angle_change.toFixed(2)} 弧度`);
}

async function bridge(bot, { blockName, count }) {
    const blockInHand = bot.inventory.items().find(item => item.name === blockName);
    if (!blockInHand) {
        console.log(`[移动] 手中没有 ${blockName} 无法搭路`);
        return;
    }
    await bot.equip(blockInHand, 'hand');
    
    bot.setControlState('sneak', true);
    for (let i = 0; i < count; i++) {
        const referenceBlock = bot.blockAt(bot.entity.position.offset(0, -1, 0));
        if (referenceBlock.name === 'air') {
            console.log("[移动] 脚下是空气，停止搭路");
            break;
        }
        await bot.placeBlock(referenceBlock, new bot.registry.Vec3(0, 1, 0)); //放置在脚下
        bot.setControlState('back', true); //慢慢后退
        await new Promise(r => setTimeout(r, 200));
        bot.setControlState('back', false);
    }
    bot.setControlState('sneak', false);
    console.log(`[移动] 搭路完成 ${count} 格`);
}

async function pillarUp(bot, { blockName, count }) {
    const blocks = bot.inventory.items().find(item => item.name === blockName);
    if (!blocks || blocks.count < count) {
        console.log(`[移动] 没有足够的 ${blockName} 来垫高 (需要 ${count}, 拥有 ${blocks?.count ?? 0})`);
        return;
    }
    await bot.equip(blocks, 'hand');

    console.log(`[移动] 开始向上垫高 ${count} 格`);
    for (let i = 0; i < count; i++) {
        bot.setControlState('jump', true);
        await bot.look(bot.entity.yaw, -Math.PI / 2, true);
        
        const referenceBlock = bot.blockAt(bot.entity.position.offset(0, -1, 0));
        try {
            await bot.placeBlock(referenceBlock, new bot.registry.Vec3(0, 1, 0));
        } 
        catch (e) {
            bot.setControlState('jump', false);
            await new Promise(r => setTimeout(r, 100));
            i--;
            continue;
        }
        bot.setControlState('jump', false);
        await bot.waitForTicks(2);
    }
    console.log(`[移动] 垫高完成`);
}

module.exports = {
    move,
    jump,
    look,
    turn,
    bridge,
    pillarUp,
};