module.exports = () => {
    console.log("正在生成训练场景: [平坦世界]");
    //创建一个200*200的草地方块平台
    for (let x = -100; x < 100; x++) {
        for (let z = -100; z < 100; z++) {
            world.setBlockStateId({ x, y: 60, z }, 2);
        }
    }
};