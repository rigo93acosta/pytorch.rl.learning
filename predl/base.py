from random import choice
import gym
from torch import Tensor


class RLBase(object):
    """
    abstracted class for reinforcement learning scripts in `pre_dr`
    """

    def __init__(self, env_name, num_episodes, alpha, gamma, policy, report_freq=100, **kwargs):
        """
        base class for RL using lookup table
        :param env_name: see https://github.com/openai/gym/wiki/Table-of-environments
        :param num_episodes: int, number of episode for training
        :param alpha: float, learning rate
        :param gamma: float, discount rate
        :param policy: str
        :param report_freq: int, by default 100
        :param kwargs: other arguments
        """
        self.env = gym.make(env_name)
        self.num_episodes = num_episodes
        self.alpha = alpha
        self.gamma = gamma
        self.state = None
        self._rewards = None
        self._policy = policy
        self.report_freq = report_freq
        for k, v in kwargs.items():
            setattr(self, str(k), v)

    def policy(self) -> int:
        """
        epsilon greedy method
        :return: action (int)
        """
        return getattr(self, self._policy)

    def schedule_alpha(self, episode: int):
        """
        schedule learning rate, this is optional
        :param episode: int
        """
        pass

    def _loop(self):
        """
        Loop in an episode. You need to implement.
        :return: total_reward (list)
        """
        raise NotImplementedError

    def train(self):
        """
        training the model
        """
        total_reward_list = []
        for episode in range(self.num_episodes):
            self.schedule_alpha(episode)
            total_reward = self._loop()
            total_reward_list.append(total_reward)

            if episode % self.report_freq == 0:
                print(f"episode:{episode:>5} total reward:{total_reward:>5.2f}")
        self._rewards = total_reward_list

    def test(self, init_state=-1):
        """
        testing the trained model
        :param init_state: the initial state
        """
        raise NotImplementedError

    __call__ = train

    @property
    def rewards(self):
        return self._rewards

    @staticmethod
    def argmax(x):
        if isinstance(x, Tensor):
            return x.max(dim=0)[1][0]
        elif isinstance(x, list):
            return x.index(max(x))


class Memory(object):
    def __init__(self, max_size=None):
        self._container = ()
        self.max_size = max_size

    def __call__(self, val):
        if self.max_size is not None and len(self._container) == self.max_size:
            self._container = self._container[1:]
        self._container += (val,)

    def __repr__(self):
        return str(self._container)

    def sample(self):
        return choice(self._container)

    @property
    def is_empty(self):
        return len(self._container) == 0
