import unittest
from dic.WordSet import WordSet


class DicWordSetTest(unittest.TestCase):

    def test_constructor(self):
        w1 = WordSet()
        w2 = WordSet('input_wordlist_test.txt')
        w3 = WordSet('input_wordlist_test.txt', 'substitution_test.txt')
        w4 = WordSet(substitution_file='substitution_test.txt')

        self.assertIsInstance(w1, WordSet)
        self.assertSetEqual(w1._content, set())
        self.assertDictEqual(w1._substitutions, {})

        self.assertIsInstance(w2, WordSet)
        self.assertSetEqual(w2._content, {'BOAT', 'TRUCK', 'DOLPHIN'})
        self.assertDictEqual(w2._substitutions, {})

        self.assertIsInstance(w3, WordSet)
        self.assertSetEqual(w3._content, {'BEAT', 'TRICK', 'DELPHINE'})
        self.assertDictEqual(
            w3._substitutions,
            {'O': 'E', 'U': 'I', 'N': 'NE'},
            )

        self.assertIsInstance(w4, WordSet)
        self.assertSetEqual(w4._content, set())
        self.assertDictEqual(
            w4._substitutions,
            {'O': 'E', 'U': 'I', 'N': 'NE'},
            )

    def test_add_substitution(self):
        w1 = WordSet()
        w1.add_substitution('$', 's')
        w1.add_substitution('o', 'I')

        w2 = WordSet(substitution_file='substitution_test.txt')
        w2.add_substitution('$', 's')
        w2.add_substitution('o', 'I')

        self.assertSetEqual(w1._substitutions, {'$': 's', 'o': 'I'})
        self.assertSetEqual(
            w2._substitutions,
            {{'O': 'I', 'U': 'I', 'N': 'NE', '$': 's'}},
            )

    def test_read_substitutions(self):
        w1 = WordSet(substitution_file='substitution_test.txt')
        w2 = WordSet()
        w3 = WordSet()

        w1.read_substitutions('substitution_test.txt')
        self.assertSetEqual(
            w1._substitutions,
            {{'O': 'I', 'U': 'I', 'N': 'NE', '$': 's'}},
            )

        w2.read_substitutions('substitution_test.txt')
        self.assertSetEqual(
            w2._substitutions,
            {{'O': 'I', 'U': 'I', 'N': 'NE', '$': 's'}},
            )

        with self.assertRaiser('SubFileException'):
            w3.read_substitutions('substitution_test_fail.txt')
