from motus.dic.WordSet import NonAplhaWordWarning, SubFileException, WordSet
import os
import tempfile
import unittest
from warnings import catch_warnings


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

    def test_add_word(self):
        w1 = WordSet()
        w2 = WordSet()
        w3 = WordSet()
        w4 = WordSet()
        self.assertSetEqual(w1._content, set())
        self.assertSetEqual(w2._content, set())
        self.assertSetEqual(w3._content, set())

        w1.add('hello ')
        self.assertSetEqual(w1._content, {'HELLO'})

        w2.add_substitution('$', 'S')
        w2.add('YE$')
        self.assertDictEqual(w2._substitutions, {'$': 'S'})
        self.assertSetEqual(w2._content, {'YES'})

        with catch_warnings(record=True) as warnings:
            w3.add('Hello!')
            self.assertSetEqual(w3._content, set())
            self.assertEqual(len(warnings), 1)
            self.assertEqual(warnings[0].category, NonAplhaWordWarning)

        with catch_warnings(record=True) as warnings:
            w4.add('Hello World')
            self.assertSetEqual(w4._content, set())
            self.assertEqual(len(warnings), 1)
            self.assertEqual(warnings[0].category, NonAplhaWordWarning)


class TestWordSetWrite(unittest.TestCase):
    def setUp(self):
        self.w = WordSet()
        self.w._content = {'SET', 'IN', 'NO', 'PARTICULAR', 'ORDER'}

        tmp_handler, tmp_path = tempfile.mkstemp()
        self.tmp_handler = tmp_handler
        self.tmp_path = tmp_path

        self.tmp_file = open(tmp_path, 'r')

    def tearDown(self):
        self.tmp_file.close()
        os.close(self.tmp_handler)


class TestWordSetWriteList(TestWordSetWrite):
    def test_write(self):
        self.w.write(self.tmp_path)
        self.assertListEqual(
            self.tmp_file.readlines(),
            ['IN\n', 'NO\n', 'ORDER\n',
                'PARTICULAR\n', 'SET\n'],
        )


class TestWordSetWriteDict(TestWordSetWrite):
    def test_write_dict(self):
        self.w.write_dict(self.tmp_path)
        self.assertListEqual(
            self.tmp_file.readlines(),
            [
                "2:\n",
                "  I:\n",
                "  - IN\n",
                "  N:\n",
                "  - 'NO'\n",       # Careful with reserved word 'NO'
                "3:\n",
                "  S:\n",
                "  - SET\n",
                "5:\n",
                "  O:\n",
                "  - ORDER\n",
                "10:\n",
                "  P:\n",
                "  - PARTICULAR\n",
            ],
        )


if __name__ == '__main__':
    unittest.main()
