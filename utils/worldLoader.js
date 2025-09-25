const path = require('path');

function loadWorldGenerator() {
  const worldName = process.argv[2] || 'flat_world';
  const generatorPath = path.join(__dirname, '..', 'training_background', `${worldName}.js`);
  
  try {
    console.log(`尝试加载世界生成脚本: ${worldName}...`);
    return require(generatorPath);
  } catch (e) {
    console.error(`错误: 找不到名为 '${worldName}' 的世界生成脚本。`);
    console.error(`请确保文件 'mc-ai/training_background/${worldName}.js' 存在。`);
    process.exit(1);
  }
}

module.exports = { loadWorldGenerator };