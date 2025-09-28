const yaml = require('js-yaml');
const fs = require('fs');
const path = require('path');

try {

    const configPath = path.join(__dirname, '..', 'config.yaml');
    const fileContents = fs.readFileSync(configPath, 'utf8');
    const config = yaml.load(fileContents);
    //导出加载的配置对象
    module.exports = config;

}
catch (e) {
    console.error("加载 config.yaml 文件失败:", e);
    process.exit(1);
}