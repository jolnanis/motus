import unittest
from unittest import mock

from motus.motus import SoloGame,  SoloRound


class SoloGameTestInstanciation(unittest.TestCase):
    def test_init(self):
        with mock.patch('motus.motus.Game.__init__') as mock_super:
            sg = SoloGame('example')
            self.assertEqual(sg.wins, 0)
            self.assertEqual(sg.rounds, 0)
            mock_super.assert_called_once_with('example', None, True)


class GameTestInstanciation(unittest.TestCase):
    def test_init(self):
        with mock.patch('motus.motus.Game.load_dic') as mock_load:
            SoloGame('example')
            mock_load.assert_called_once_with('example', None, True)


class SoloGameTestBasic(unittest.TestCase):
    def setUp(self):
        self.sg = SoloGame('example')


class SoloGameTestIncr(SoloGameTestBasic):
    def _test_incr_wins(self, initial, expected):
        self.sg.wins = initial[0]
        self.sg.rounds = initial[1]
        self.sg.incr_wins()
        self.assertEqual(self.sg.wins, expected[0])
        self.assertEqual(self.sg.rounds, expected[1])

    def _test_incr_rounds(self, initial, expected):
        self.sg.wins = initial[0]
        self.sg.rounds = initial[1]
        self.sg.incr_rounds()
        self.assertEqual(self.sg.wins, expected[0])
        self.assertEqual(self.sg.rounds, expected[1])

    def test_incr_wins(self):
        self._test_incr_wins([0, 0], [1, 0])
        self._test_incr_wins([12, 13], [13, 13])

    def test_incr_rounds(self):
        self._test_incr_rounds([0, 0], [0, 1])
        self._test_incr_rounds([12, 13], [12, 14])


class SoloRoundTestBasic(SoloGameTestBasic):
    def setUp(self):
        with mock.patch('motus.motus.Game.__init__'):
            self.sg = SoloGame('example')


class SoloRoundTestInstanciation(SoloRoundTestBasic):
    def test_init(self):
        with mock.patch('motus.motus.Round.pick_solution') as pick_mock:
            rd = SoloRound(self.sg, 8)
            pick_mock.assert_called_once_with()
            self.assertEqual(rd.wordlength, 8)


if __name__ == '__main__':
    unittest.main()
