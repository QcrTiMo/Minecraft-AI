const PLATFORM_SIZE = 40; //80x80的训练场
const WALL_COUNT = 15;    //15堵墙
const PIT_COUNT = 20;     //20个坑

//在指定范围内生成一个随机整数
function randInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

//生成一堵墙
function generateWall(world) {
  const startX = randInt(-PLATFORM_SIZE, PLATFORM_SIZE);
  const startZ = randInt(-PLATFORM_SIZE, PLATFORM_SIZE);
  const length = randInt(5, 15);
  const orientation = Math.random() < 0.5 ? 'x' : 'z'; //随机决定墙是横向还是纵向

  for (let i = 0; i < length; i++) {
    const x = orientation === 'x' ? startX + i : startX;
    const z = orientation === 'z' ? startZ + i : startZ;
    
    //确保墙不会超出平台边界
    if (Math.abs(x) < PLATFORM_SIZE && Math.abs(z) < PLATFORM_SIZE) {
      world.setBlockStateId({ x, y: 61, z }, 1); //一格高的石头墙
    }
  }
}

//挖一个坑
function generatePit(world) {
    const centerX = randInt(-PLATFORM_SIZE + 2, PLATFORM_SIZE - 2);
    const centerZ = randInt(-PLATFORM_SIZE + 2, PLATFORM_SIZE - 2);
    const sizeX = randInt(1, 3);
    const sizeZ = randInt(1, 3);

    for (let x = -Math.floor(sizeX/2); x < Math.ceil(sizeX/2); x++) {
        for (let z = -Math.floor(sizeZ/2); z < Math.ceil(sizeZ/2); z++) {
            //将平台方块替换为空气(ID 0)
            world.setBlockStateId({ x: centerX + x, y: 60, z: centerZ + z }, 0);
        }
    }
}


module.exports = () => (world) => {
  console.log("正在生成世界: [高级障碍训练场]");

  //生成基础平台
  for (let x = -PLATFORM_SIZE; x < PLATFORM_SIZE; x++) {
    for (let z = -PLATFORM_SIZE; z < PLATFORM_SIZE; z++) {
      world.setBlockStateId({ x, y: 60, z }, 2);
    }
  }

  //生成墙壁
  for (let i = 0; i < WALL_COUNT; i++) {
    generateWall(world);
  }

  //生成坑洞
  for (let i = 0; i < PIT_COUNT; i++) {
    generatePit(world);
  }
};