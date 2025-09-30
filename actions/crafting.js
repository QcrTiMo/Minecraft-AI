async function craftItem(bot, { itemName, count = 1, craftingTable = null }) {
    const mcData = require('minecraft-data')(bot.version);
    const item = mcData.itemsByName[itemName];
    if (!item) {
        console.log(`[合成] 未知物品: ${itemName}`);
        return;
    }
    
    const recipe = bot.recipesFor(item.id, null, 1, craftingTable)[0];
    if (!recipe) {
        console.log(`[合成] 找不到 ${itemName} 的配方`);
        return;
    }

    try {
        await bot.craft(recipe, count, craftingTable);
        console.log(`[合成] 成功合成了 ${count} 个 ${itemName}`);
    } catch (err) {
        console.error(`[合成] 合成 ${itemName} 失败: ${err.message}`);
    }
}

module.exports = {
    craftItem,
};