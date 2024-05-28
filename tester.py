import gym
import random
import stable_baselines3
import time

gym.envs.registration.register(
    id='PlaneGame-v0',
    entry_point='environnement:PlaneGameEnv',  # Update this with the actual module path
)

env = gym.make('PlaneGame-v0')
env.reset()

model = stable_baselines3.PPO.load("myModel", env = env)

env.startRendering()

while True:
  env.render()
  obs, reward, done, info = env.step(model.predict(env.getState())[0])
  #print(obs, "\n", reward, "\n",done,  "\n", info)
  if(env.gameOver):
    time.sleep(10)
    env.reset()
  time.sleep(0.05)

  env.closeIfQuit()

print(env.step(2))