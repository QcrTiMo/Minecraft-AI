async function digBlock(bot, {x, y, z}){
    const targetBlock = bot.blockAt(new Vec3(x, y, z));
    if (targetBlock){
        console.log(`动作: 开始挖掘位于 (${x},${y},${z}) 的 ${targetBlock.name}`);
        await bot.dig(targetBlock);
        console.log(`动作: 挖掘完成`);
    }
    else{
        console.error(`动作: 未找到位于 (${x},${y},${z}) 的方块`);
    }
}

async function placeBlock(bot, {x, y, z, blockName}){
    //需要Bot手持物品方块
    console.log(`动作: 开始在 (${x},${y},${z}) 放置 ${blockName}(TODO)`);
}

async function attack(bot, {entityId}){
    const targetEntity = bot.entities[entityId];
    if (targetEntity){
        console.log(`动作: 攻击实体 ${targetEntity.displayName}`);
        await bot.attack(targetEntity);
    }
    else{
        console.error(`动作: 未找到ID为 ${entityId} 的实体`);
    }
}

module.exports = {
    digBlock,
    placeBlock,
    attack,
    //TODO
}