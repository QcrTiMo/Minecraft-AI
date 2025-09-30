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

async function smeltItem(bot, { furnaceBlock, inputItemName, fuelItemName, count }) {
    const mcData = require('minecraft-data')(bot.version);

    //查找物品ID
    const inputItem = mcData.itemsByName[inputItemName];
    const fuelItem = mcData.itemsByName[fuelItemName];
    if (!inputItem || !fuelItem) {
        console.log(`[交互] 无效的物品名称: ${inputItemName} 或 ${fuelItemName}`);
        return;
    }

    console.log(`[交互] 开始熔炼 ${count} 个 ${inputItemName} 使用 ${fuelItemName}`);
    const furnace = await bot.openFurnace(furnaceBlock);

    for (let i = 0; i < count; i++) {
        //放入原料
        await furnace.putInput(inputItem.id, null, 1);
        //检查一下燃料槽是否为空
        if (!furnace.fuelItem() || furnace.fuel < 0.1) {
            await furnace.putFuel(fuelItem.id, null, 1);
        }
        
        await new Promise(resolve => {
            const listener = () => {
                if (furnace.outputItem()) {
                    furnace.off('update', listener);
                    resolve();
                }
            };
            furnace.on('update', listener);
        });

        //取出成品
        await furnace.takeOutput();
        console.log(`[交互] 已成功熔炼 1 个，剩余 ${count - 1 - i} 个`);
    }

    await furnace.close();
    console.log('[交互] 熔炼任务完成');
}

async function placeItem(bot, { itemName, referenceBlock, faceVector }) {
    const item = bot.inventory.items().find(i => i.name === itemName);
    if (!item) {
        console.log(`[交互] 物品栏中没有 ${itemName}`);
        return;
    }
    //装备物品
    await bot.equip(item, 'hand');

    //看向要放置的位置
    const placePosition = referenceBlock.position.plus(faceVector);
    await bot.lookAt(placePosition);

    //激活物品(倒水)
    bot.activateItem();
    console.log(`[交互] 在 ${placePosition} 处使用了 ${itemName}`);
    await new Promise(resolve => setTimeout(resolve, 200));
}

module.exports = {
    mineBlock,
    placeBlock,
    useBlock,
    eatFood,
    smeltItem,
    placeItem,
};