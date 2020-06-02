import unittest
from unittest import mock

from motus.dictools import Dic, new_dic

EMPTY_LIST = []
LIST_OF_WORDS = ['ASPIC', 'APRES', 'ARRET', 'ACTIF', 'ANNEE']
DICT_OF_SAME_LENGTH = {
    'A': ['ASPIC', 'APRES', 'ARRET', 'ACTIF', 'ANNEE'],
    'B': ['BELLE', 'BIERE', 'BUTTE'],
    'C': ['COUPS', 'CLAIR', 'COUPE', 'CERNE'],
}
FULL_DIC = {
    5: {
        'A': ['ASPIC', 'APRES', 'ARRET', 'ACTIF', 'ANNEE'],
        'B': ['BELLE', 'BIERE', 'BUTTE'],
        'C': ['COUPS', 'CLAIR', 'COUPE', 'CERNE'],
    },

    6: {
        'M': ['MOUCHE', 'MAIGRE', 'MIETTE'],
        'P': ['PIERRE', 'PLUMES', 'PITRES'],
        'S': ['SALVES', 'SAUCES'],
    },
}
FAKE_FULL_DIC = {
    3: ['ART', 'AUX', 'ANS', 'AIR'],
    5: ['ASPIC', 'APRES', 'ARRET', 'ACTIF', 'ANNEE'],
}
LIST_SAME_LENGTH = [
    'ASPIC', 'APRES', 'ARRET', 'ACTIF', 'ANNEE', 'BELLE', 'BIERE',
    'BUTTE', 'COUPS', 'CLAIR', 'COUPE', 'CERNE',
]
LIST_FULL_DIC = [
    'ASPIC', 'APRES', 'ARRET', 'ACTIF', 'ANNEE', 'BELLE', 'BIERE',
    'BUTTE', 'COUPS', 'CLAIR', 'COUPE', 'CERNE', 'MOUCHE', 'MAIGRE',
    'MIETTE', 'PIERRE', 'PLUMES', 'PITRES', 'SALVES', 'SAUCES',
]


class DictoolsTestNewDic(unittest.TestCase):
    def _test_new_dic_direct(self, *args, **kwargs):
        with mock.patch('motus.dictools.Dic') as init:
            new_dic(*args, **kwargs)

            init.assert_called_once_with()

    def _test_new_dic_through_reader(self, *args, **kwargs):
        expected = kwargs.pop('expected')
        with mock.patch('motus.dictools.Reader') as rd:
            new_dic(*args, **kwargs)
            print(rd.mock_calls)
            self.assertEqual(len(rd.mock_calls), 2)
            self.assertEqual(rd.mock_calls, expected)

    def test_new_dir_no_args(self):
        self._test_new_dic_direct()

    def test_new_dic_good_args(self):
        self._test_new_dic_through_reader(
            dic_path='example.yml',
            expected=[
                mock.call(),
                mock.call().config(dic_path='example.yml'),
            ]
        )
        self._test_new_dic_through_reader(
            'example.yml',
            dic_path='example.yml',
            expected=[
                mock.call(),
                mock.call().config('example.yml', dic_path='example.yml')
            ]
        )
        self._test_new_dic_through_reader(
            'example.yml',
            expected=[
                mock.call(),
                mock.call().config('example.yml')
            ]
        )
        self._test_new_dic_through_reader(
            dic_path='ex.txt',
            config='cfg.txt',
            expected=[
                mock.call(), mock.call().config(
                    dic_path='ex.txt',
                    config='cfg.txt',
                )
            ]
        )

    def test_new_dic_other_kwargs(self):
        self._test_new_dic_direct(config='cfg.txt', pckg=False)
        self._test_new_dic_direct(dic_patch='cfg.txt')


class DictoolsTestDicInstanciation(unittest.TestCase):

    def _test_dic_init(self, *args, **kwargs):
        d = Dic(*args, **kwargs)

        self.assertIsInstance(d, Dic)
        self.assertEqual(d.content, {})
        self.assertEqual(d._state_flag, True)
        self.assertEqual(d._words_flag, True)

    def test_dic_init(self):
        self._test_dic_init()

    def test_dic_init_failing(self):
        with self.assertRaises(TypeError):
            self._test_dic_init('arg')

        with self.assertRaises(TypeError):
            self._test_dic_init(kw='arg')

        with self.assertRaises(TypeError):
            self._test_dic_init('args', 'and', kw='arg')


class DictoolsTestDicState(unittest.TestCase):
    def _test_dic_state(self, content, predicted):
        self.d = Dic()
        self.d.content = content
        self.assertTrue(self.d._state_flag)
        self.assertEqual(self.d.content, content)

        self.assertEqual(self.d.state, predicted)
        self.assertFalse(self.d._state_flag)

    def test_dict_state(self):
        self._test_dic_state(EMPTY_LIST, 'empty')
        self._test_dic_state(LIST_OF_WORDS, 'list of words')
        self._test_dic_state(DICT_OF_SAME_LENGTH, 'various-initials dict')
        self._test_dic_state(FULL_DIC, 'various-lengths dict')
        # Is imported even though not valid :
        self._test_dic_state(FAKE_FULL_DIC, 'various-lengths dict')


class DictoolsTestDicWords(unittest.TestCase):
    def _test_dic_words(self, content, predicted):
        self.d = Dic()
        self.d.content = content
        self.assertTrue(self.d._words_flag)
        self.assertEqual(self.d.content, content)

        self.assertEqual(self.d.words, predicted)
        self.assertFalse(self.d._words_flag)

    def test_dict_words(self):
        self._test_dic_words(EMPTY_LIST, EMPTY_LIST)
        self._test_dic_words(LIST_OF_WORDS, LIST_OF_WORDS)
        self._test_dic_words(DICT_OF_SAME_LENGTH, LIST_SAME_LENGTH)
        self._test_dic_words(FULL_DIC, LIST_FULL_DIC)

    def test_dict_words_failing(self):
        with self.assertRaises(TypeError):
            self._test_dic_words(FAKE_FULL_DIC, [])


if __name__ == '__main__':
    unittest.main()
