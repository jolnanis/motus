from dic.WordSet import WordSet
from dic.WordSet import SubFileException
import os
import unittest

SAMPLE_DATA_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                'sample_data/')
SUBSTITUTION_FILE = os.path.join(SAMPLE_DATA_PATH, 'substitution.txt')
SUBSTITUTION_BROKEN_FILE = os.path.join(SAMPLE_DATA_PATH,
                                        'substitution_broken.txt')
WORDLIST_FILE = os.path.join(SAMPLE_DATA_PATH, 'wordlist.txt')
# WORDLIST_BROKEN_FILE = os.path.join(SAMPLE_DATA_PATH, 'wordlist_broken.txt')


class DicWordSetTest(unittest.TestCase):
    def test_constructor(self):
        w1 = WordSet()
        w2 = WordSet(WORDLIST_FILE)
        w3 = WordSet(WORDLIST_FILE, SUBSTITUTION_FILE)
        w4 = WordSet(substitution_file=SUBSTITUTION_FILE)

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

        w2 = WordSet(substitution_file=SUBSTITUTION_FILE)
        w2.add_substitution('$', 's')
        w2.add_substitution('o', 'I')

        self.assertDictEqual(w1._substitutions, {'$': 'S', 'O': 'I'})
        self.assertDictEqual(
            w2._substitutions,
            {'O': 'I', 'U': 'I', 'N': 'NE', '$': 'S'},
            )

    def test_read_substitutions(self):
        w1 = WordSet(substitution_file=SUBSTITUTION_FILE)
        w2 = WordSet()
        w3 = WordSet()

        w1.read_substitutions(SUBSTITUTION_FILE)
        self.assertDictEqual(
            w1._substitutions,
            {'O': 'E', 'U': 'I', 'N': 'NE'},
            )

        w2.read_substitutions(SUBSTITUTION_FILE)
        self.assertDictEqual(
            w2._substitutions,
            {'O': 'E', 'U': 'I', 'N': 'NE'},
            )

        with self.assertRaises(SubFileException):
            w3.read_substitutions(SUBSTITUTION_BROKEN_FILE)


if __name__ == '__main__':
    unittest.main()
