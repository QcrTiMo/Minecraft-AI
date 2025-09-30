const combat = require('./combat');
const crafting = require('./crafting');
const interaction = require('./interaction');
const inventory = require('./inventory');
const movement = require('./movement');
const perception = require('./perception');
const tp = require('./tp');

const actions = {
    ...combat,
    ...crafting,
    ...interaction,
    ...inventory,
    ...movement,
    ...perception,
    ...tp,
};

async function executeAction(bot, name, args) {
    if (actions[name]) {
        try {
            return await actions[name](bot, args);
        } catch (error) {
            console.error(`执行动作 '${name}' 时发生错误:`, error);
            throw error;
        }
    } else {
        console.error(`未知动作: ${name}`);
        throw new Error(`Unknown action: ${name}`);
    }
}

module.exports = {
    executeAction,
    ...actions,
};