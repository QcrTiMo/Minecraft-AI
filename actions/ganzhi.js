function getBotStatus(bot) {
    return {
        health: bot.health,
        food: bot.food,
        saturation: bot.foodSaturation,
        oxygen: bot.oxygenLevel,
        position: bot.entity.position,
        velocity: bot.entity.velocity,
        yaw: bot.entity.yaw,
        pitch: bot.entity.pitch,
        onGround: bot.entity.onGround,
        isSleeping: bot.isSleeping,
        isRaining: bot.isRaining,
        timeOfDay: bot.time.timeOfDay,
        level: bot.experience.level,
        inventory: bot.inventory.items().map(item => ({
            name: item.name,
            count: item.count,
            slot: item.slot
        })),
        heldItem: bot.heldItem ? { name: bot.heldItem.name, count: bot.heldItem.count } : null,
    };
}

async function findNearestBlock(bot, { name, maxDistance = 32 }) {
    const mcData = require('minecraft-data')(bot.version);
    const blockId = mcData.blocksByName[name]?.id;

    if (!blockId) {
        console.log(`[感知] 未知方块名称: ${name}`);
        return null;
    }
    const options = {
        matching: blockId,
        maxDistance: maxDistance,
        count: 1
    };
    const block = bot.findBlock(options);
    return block;
}

function findNearestEntity(bot, { type, name, maxDistance = 32 }) {
    const filter = (entity) => {
        let match = entity.type === type && bot.entity.position.distanceTo(entity.position) <= maxDistance;
        if (match && name) {
            match = entity.name.toLowerCase() === name.toLowerCase();
        }
        return match && entity !== bot.entity;
    };
    return bot.nearestEntity(filter);
}

module.exports = {
    getBotStatus,
    findNearestBlock,
    findNearestEntity,
};