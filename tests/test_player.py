import unittest

from motus.player import (BotPlayer, HumanPlayer, Player,
                          RandomStrategy, Strategy)


class PlayerTestInstanciation(unittest.TestCase):
    def test_init_abc(self):
        with self.assertRaises(TypeError):
            Player()


class PlayerTestMatches(unittest.TestCase):
    def _test_matches(self, solution, guess, hint_string, right_ans):
        ans = Player.matches(solution, guess, hint_string)
        self.assertEqual(ans, right_ans)

    def test_correct_1(self):
        self._test_matches('BANANA', 'BANANA', 'RRRRRR', True)

    def test_correct_2(self):
        self._test_matches('BANANA', 'BOUNTY', 'RWWMWW', True)

    def test_incorrect_1(self):
        self._test_matches('BANANA', 'BANANA', 'RRWRRR', False)

    def test_incorrect_2(self):
        self._test_matches('BANANA', 'BOUNTY', 'RWWWMW', False)


class PlayerTestClassMethods(unittest.TestCase):
    def test_give_hint_1(self):
        Player.universe = ['BANANA', 'BAMBOO', 'BIKINI', 'BOUNTY']
        Player.give_hint('BOUNTY', 'RWWMWW')
        self.assertAlmostEqual(Player.universe, ['BANANA', 'BIKINI'])


class HumanPlayerTestInstanciation(unittest.TestCase):
    def test_init_abc(self):
        self.assertIsInstance(HumanPlayer(), (HumanPlayer, Player))


class HumanPlayerTestGuess(unittest.TestCase):
    pass


class BotPlayerTestInstatnciation(unittest.TestCase):
    def test_init(self):
        strat = RandomStrategy()
        self.assertIsInstance(BotPlayer(strat), (BotPlayer, Player))


class StrategyTestInit(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(TypeError):
            Strategy()


class RandomStrategyTestInit(unittest.TestCase):
    def test_init(self):
        self.assertIsInstance(RandomStrategy(), RandomStrategy, Strategy)


class RandomStrategyTestGuess(unittest.TestCase):
    def setUp(self):
        self.strat = RandomStrategy()

    def test_guess_in_universe(self):
        universe = ['BANANA', 'BAMBOO', 'BIKINI', 'BOUNTY']
        self.assertIn(self.strat.guess(universe), universe)