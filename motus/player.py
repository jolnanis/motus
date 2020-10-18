from abc import ABC, abstractmethod
import random

from motus import motus
from motus.ui import UI


class Player(ABC):
    universe = None

    def __init__(self):
        pass

    @classmethod
    def matches(cls, word, guess, hint_string):
        """ Checks if a word matches a rule given by a combination of
        a guess and corresponding hint_sting"""
        return motus.evaluate(word, guess)[1] == hint_string

    @classmethod
    def give_hint(cls, guess, hint_string):
        """ Updates the universe of possible words for all the players """
        cls.universe = [word for word in cls.universe
                        if cls.matches(word, guess, hint_string)]

    @abstractmethod
    def guess(self):
        pass


class HumanPlayer(Player):
    def __init__(self):
        super().__init__()

    def guess(self):
        return UI.prompt_guess()


class BotPlayer(Player):
    def __init__(self, strategy):
        self.strategy = strategy
        super().__init__()

    def guess(self):
        return self.strategy.guess(type(self).universe)


class Strategy(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def guess(self, universe):
        """ Returns a guess based on the universe of all possible words"""
        pass


class RandomStrategy(Strategy):
    def guess(self, universe):
        k = random.randint(0, len(universe)-1)
        return universe[k]
