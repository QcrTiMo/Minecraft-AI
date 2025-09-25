const PLATFORM_SIZE = 40;
const OBSTACLE_COUNT = 70;

module.exports = () => (world) => {
    console.log("正在生成训练场景: [简单障碍物]");
    //先生成一个基础平台
  for (let x = -PLATFORM_SIZE; x < PLATFORM_SIZE; x++) {
    for (let z = -PLATFORM_SIZE; z < PLATFORM_SIZE; z++) {
      world.setBlockStateId({ x, y: 60, z }, 2);
    }
  }

  //在平台上随机放置一格高的障碍物(石头, ID 1)
  for (let i = 0; i < OBSTACLE_COUNT; i++) {
    const x = Math.floor(Math.random() * (PLATFORM_SIZE * 2)) - PLATFORM_SIZE;
    const z = Math.floor(Math.random() * (PLATFORM_SIZE * 2)) - PLATFORM_SIZE;
    //在y=61的高度放置石头
    world.setBlockStateId({ x, y: 61, z }, 1);
  }
}