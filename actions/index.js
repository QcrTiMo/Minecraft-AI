const movementActions = require('./movement');
const interactionActions = require('./interaction');

const allActions = {
    ...movementActions,
    ...interactionActions,
};

module.exports = async function handlAction(bot, action){
    const {name, params} = action;
    const actionFunction = allActions[name];

    if (actionFunction){
        try{
            await actionFunction(bot, params);
        }
        catch(err){
            console.error(`执行动作 ${name} 时出错:`, err.message);
        }
    }
    else{
        console.warn(`未知动作: ${name}`);
    }
}