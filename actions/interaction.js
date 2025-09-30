async function mineBlock(bot, { block }) {
    if (!block) {
        console.log("[交互] 无效的挖掘目标");
        return;
    }
    //TODO
    if (bot.canDigBlock(block)) {
        console.log(`[交互] 开始挖掘 ${block.name}`);
        await bot.dig(block);
        console.log(`[交互] 完成挖掘 ${block.name}`);
    }
    else {
        console.log(`[交互] 无法挖掘 ${block.name}`);
    }
}

async function placeBlock(bot, { blockName, position }) {
    const blockInHand = bot.inventory.items().find(item => item.name === blockName);
    if (!blockInHand) {
        console.log(`[交互] 手中没有 ${blockName}`);
        return;
    }
    await bot.equip(blockInHand, 'hand');
    
    const referenceBlock = bot.blockAt(position.offset(0, -1, 0));
    await bot.placeBlock(referenceBlock, new bot.registry.Vec3(0, 1, 0));
    console.log(`[交互] 在 ${position} 放置了 ${blockName}`);
}

async function useBlock(bot, { block }) {
    if (!block) {
        console.log("[交互] 无效的使用目标");
        return;
    }
    console.log(`[交互] 正在使用 ${block.name}`);
    await bot.activateBlock(block);
}

async function eatFood(bot) {
    const mcData = require('minecraft-data')(bot.version);
    //找到最有营养的食物
    const food = bot.inventory.items().sort((a, b) => {
        const foodA = mcData.foods[a.type];
        const foodB = mcData.foods[b.type];
        return (foodB?.foodPoints ?? 0) - (foodA?.foodPoints ?? 0);
    })[0];
    
    if (!food || !mcData.foods[food.type]) {
        console.log("[交互] 没有食物可以吃");
        return;
    }

    await bot.equip(food, 'hand');
    console.log(`[交互] 正在吃 ${food.name}`);
    await bot.consume();
    console.log(`[交互] 吃完了 ${food.name}`);
}

module.exports = {
    mineBlock,
    placeBlock,
    useBlock,
    eatFood,
};