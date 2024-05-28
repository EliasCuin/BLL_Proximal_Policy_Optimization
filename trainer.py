import gym
import random
import stable_baselines3

gym.envs.registration.register(
    id='PlaneGame-v0',
    entry_point='gpttest:PlaneGameEnv',  # Update this with the actual module path
)

env = gym.make('PlaneGame-v0')
env.reset()

# model = stable_baselines3.PPO("MlpPolicy", env, verbose=1)
model = stable_baselines3.PPO.load("myModel", env = env)

print(env.getState())
print(model.policy.mlp_extractor.policy_net)
print(model.policy.mlp_extractor.value_net)


for i in range(100_000):
  model.save("myModel")
  print(i)
  model.learn(total_timesteps=10_000, reset_num_timesteps=False)

print("e")
env.startRendering()

while True:
  env.render()
  obs, reward, done, info = env.step(model.predict(env.getState())[0])
  print(obs, "\n", reward, "\n",done,  "\n", info)
  if(env.gameOver):
    env.reset()

  env.closeIfQuit()

print(env.step(2))