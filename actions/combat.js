async function attack(bot, { targetEntity }) {
    if (!targetEntity) {
        console.log('[战斗] 无效的攻击目标');
        return;
    }
    console.log(`[战斗] 正在攻击 ${targetEntity.name || targetEntity.username}`);
    await bot.attack(targetEntity);
}

async function shoot(bot, { targetEntity }) {
    if (!targetEntity) {
        console.log('[战斗] 无效的射击目标');
        return;
    }
    
    //装备弓
    const bow = bot.inventory.items().find(item => item.name.includes('bow'));
    if (!bow) {
        console.log('[战斗] 物品栏内没有弓');
        return;
    }
    await bot.equip(bow, 'hand');
    console.log(`[战斗] 已装备弓，准备射击 ${targetEntity.name}`);

    //激活弓
    bot.activateItem();
    //蓄力大约需要1秒
    const aimDuration = 1200; //1.2秒
    const startTime = Date.now();
    while (Date.now() - startTime < aimDuration) {
        await bot.lookAt(targetEntity.position.offset(0, targetEntity.height * 0.8, 0)); //瞄准身体上半部分
        await new Promise(resolve => setTimeout(resolve, 50));
    }
    
    //停止激活
    bot.deactivateItem();
    console.log(`[战斗] 已向 ${targetEntity.name} 射出一箭`);
}

module.exports = {
    attack,
    shoot,
};