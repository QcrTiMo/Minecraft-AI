async function equipItem(bot, { itemName, destination }) {
    const item = bot.inventory.items().find(i => i.name === itemName);
    if (!item) {
        console.log(`[库存] 找不到物品 ${itemName}`);
        return;
    }
    try {
        await bot.equip(item, destination);
        console.log(`[库存] 已将 ${itemName} 装备到 ${destination}`);
    } catch (err) {
        console.error(`[库存] 装备 ${itemName} 失败: ${err.message}`);
    }
}

/**
 * 丢弃指定数量的物品
 * @param {object} bot
 * @param {object} options
 * @param {string} options.itemName - 物品名称
 * @param {number} [options.count=1] - 丢弃数量
 */
async function tossItem(bot, { itemName, count = 1 }) {
    const item = bot.inventory.items().find(i => i.name === itemName);
    if (!item) {
        console.log(`[库存] 找不到物品 ${itemName}`);
        return;
    }
    await bot.toss(item.type, null, count);
    console.log(`[库存] 丢弃了 ${count} 个 ${itemName}`);
}

/**
 * 将手中的物品放到快捷栏的指定格子
 * @param {object} bot
 * @param {object} options
 * @param {number} options.slot - 快捷栏格子(0-8)
 */
async function selectHotbarSlot(bot, { slot }) {
    if (slot < 0 || slot > 8) {
        console.log(`[库存] 无效的快捷栏格子: ${slot}`);
        return;
    }
    bot.setQuickBarSlot(slot);
    console.log(`[库存] 已选择快捷栏第 ${slot} 格`);
}

module.exports = {
    equipItem,
    tossItem,
    selectHotbarSlot,
};