import minedojo

env = minedojo.make(
    task_id="harvest_wool_with_shears_and_sheep",
    image_size=(160, 256)
)
obs = env.reset()
for i in range(50):
    act = env.action_space.no_op()
    act[0] = 1    # forward/backward
    if i % 10 == 0:
        act[2] = 1    # jump
    obs, reward, done, info = env.step(act)
env.close()