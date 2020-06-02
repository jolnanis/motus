import io
import os
import unittest
from unittest import mock
import tempfile

from motus import dictools
from motus.dictools import FileHandler, Reader, Writer


DIC = 'motus.dictools.Dic'
FILE_HANDLER = 'motus.dictools.FileHandler'
READER = 'motus.dictools.Reader'
WRITER = 'motus.dictools.Writer'


class DictoolsTestReaderInstanciation(unittest.TestCase):
    def _test_reader_instanciation(self, *args, **kwargs):
        """`expected`: expected mock.call for Reader.config()"""
        if 'expected' in list(kwargs):
            expected = kwargs.pop('expected')
        else:
            expected = None

        with mock.patch(f'{FILE_HANDLER}.__init__') as fd_mock:
            with mock.patch(f'{READER}.config') as cfg_mock:
                rd = Reader(*args, **kwargs)

                self.assertIsInstance(rd, FileHandler)
                self.assertIsInstance(rd, Reader)
                self.assertEqual(rd._substitutions, dict())
                fd_mock.assert_called_once_with()
                cfg_mock.assert_called_once()
                if expected is not None:
                    self.assertEqual(cfg_mock.call_args, expected)

    def test_reader_instanciation_1(self):
        self._test_reader_instanciation()

    def test_reader_instanciation_2(self):
        self._test_reader_instanciation(
            'path_to_dic',
            expected=mock.call('path_to_dic'),
        )

    def test_reader_instanciation_3(self):
        self._test_reader_instanciation(
            'path_to_dic',
            'filetype',
            expected=mock.call('path_to_dic', 'filetype'),
        )

    def test_reader_instanciation_4(self):
        self._test_reader_instanciation(
            'path/to/dic.yml',
            'application/x-yaml',
            'config.txt',
            False,
            expected=(
                mock.call('path/to/dic.yml', 'application/x-yaml',
                          'config.txt', False,)
            )
        )

    def test_reader_instanciation_5(self):
        self._test_reader_instanciation(
            config='cfg.txt',
            dic_path='path/to/dic.txt',
            expected=(
                mock.call(config='cfg.txt',
                          dic_path='path/to/dic.txt')
            )
        )


EMPTY_LIST = []
EMPTY_LIST_TXT = ['\n']
EMPTY_LIST_YML = ['\n']

LIST_OF_WORDS = ['ASPIC', 'APRES', 'ARRET', 'ACTIF', 'ANNEE']
LIST_OF_WORDS_TXT = [
    'ASPIC\n',
    'APRES\n',
    'ARRET\n',
    'ACTIF\n',
    'ANNEE\n',
]
LIST_OF_WORDS_YML = [
    '- ASPIC\n',
    '- APRES\n',
    '- ARRET\n',
    '- ACTIF\n',
    '- ANNEE\n',
]

DICT_OF_SAME_LENGTH = {
    'A': ['ASPIC', 'ANNEE'],
    'B': ['BELLE', 'BIERE', 'BUTTE'],
    'C': ['COUPS'],
}
DICT_OF_SAME_LENGTH_TXT = [
    'ASPIC\n',
    'ANNEE\n',
    'BELLE\n',
    'BIERE\n',
    'BUTTE\n',
    'COUPS\n',
]
DICT_OF_SAME_LENGTH_YML = [
    'A:\n',
    '- ASPIC\n',
    '- ANNEE\n',
    'B:\n',
    '- BELLE\n',
    '- BIERE\n',
    '- BUTTE\n',
    'C:\n',
    '- COUPS\n',
]

FULL_DIC = {
    5: {
        'A': ['ASPIC', 'ANNEE'],
        'B': ['BELLE', 'BIERE', 'BUTTE'],
        'C': ['COUPS'],
    },

    6: {
        'M': ['MOUCHE'],
        'S': ['SAUCES'],
    },
}
FULL_DIC_TXT = [
    'ASPIC\n',
    'ANNEE\n',
    'BELLE\n',
    'BIERE\n',
    'BUTTE\n',
    'COUPS\n',
    'MOUCHE\n',
    'SAUCES\n',
]
FULL_DIC_YML = [
    '5:\n',
    '  A:\n',
    '  - ASPIC\n',
    '  - ANNEE\n',
    '  B:\n',
    '  - BELLE\n',
    '  - BIERE\n',
    '  - BUTTE\n',
    '  C:\n',
    '  - COUPS\n',
    '6:\n',
    '  M:\n',
    '  - MOUCHE\n',
    '  S:\n',
    '  - SAUCES\n',
]

FAKE_FULL_DIC = {
    3: ['ART', 'ANS', 'AIR'],
    5: ['ASPIC', 'APRES', 'ARRET'],
}
FAKE_FULL_DIC_TXT = [
    'ART\n',
    'ANS\n',
    'AIR\n',
    'ASPIC\n',
    'APRES\n',
    'ARRET\n',
]
FAKE_FULL_DIC_YML = [
    '3:\n',
    '- ART\n',
    '- ANS\n',
    '- AIR\n',
    '5:\n',
    '- ASPIC\n',
    '- APRES\n',
    '- ARRET\n',
]


class DictoolsTestReaderBasic(unittest.TestCase):
    def setUp(self):
        self.rd = Reader()


class DictoolsTestReaderConfig(DictoolsTestReaderBasic):
    def _test_reader_config(self, *args, **kwargs):
        """`expected`: expected mock.call for Reader.config()"""
        if 'expected_sub' in list(kwargs):
            expected_sub = kwargs.pop('expected_sub')
        else:
            expected_sub = None

        if 'expected_super' in list(kwargs):
            expected_super = kwargs.pop('expected_super')
        else:
            expected_super = None

        if 'pckg' in list(kwargs):
            pckg = kwargs.pop('pckg')
        elif len(args) >= 4:
            pckg = args[3]
        else:
            pckg = None

        with mock.patch(f'{READER}._config_substitutions') as sub_mock:
            with mock.patch(f'{FILE_HANDLER}.config') as super_mock:
                self.rd.config(*args, **kwargs)

                super_mock.assert_called_once()
            if pckg is not None:
                self.assertEqual(self.rd.pckg, pckg)
            if expected_sub is not None:
                sub_mock.assert_called_once()
                self.assertEqual(sub_mock.call_args, expected_sub)
            if expected_super is not None:
                self.assertEqual(super_mock.call_args, expected_super)

    def test_reader_config_1(self):
        self._test_reader_config()

    def test_reader_config_2(self):
        self._test_reader_config(
            'path_to_dic',
            expected_super=mock.call('path_to_dic', None),
        )

    def test_reader_config_3(self):
        self._test_reader_config(
            'path_to_dic',
            'filetype',
            expected_super=mock.call('path_to_dic', 'filetype'),
        )

    def test_reader_config_4(self):
        self._test_reader_config(
            'path/to/dic.yml',
            'application/x-yaml',
            'config.txt',
            False,
            expected_super=(
                mock.call('path/to/dic.yml', 'application/x-yaml')
            ),
            expected_sub=(
                mock.call('config.txt')
            ),
        )

    def test_reader_config_5(self):
        self._test_reader_config(
            config='cfg.txt',
            dic_path='path/to/dic.txt',
            expected_super=(
                mock.call('path/to/dic.txt', None)
            ),
            expected_sub=(
                mock.call('cfg.txt')
            ),
        )


class DictoolsTestReaderAddSubstitution(DictoolsTestReaderBasic):
    def setUp(self):
        super().setUp()
        self.assertEqual(self.rd._substitutions, dict())

    def test_add_substitions_to_empty(self):
        self.rd.add_substitution('é', 'e')
        self.assertEqual(self.rd._substitutions, {'É': 'E'})

    def test_add_substitions_to_existing(self):
        self.rd._substitutions = {'É': 'E'}
        self.rd.add_substitution('Ê', 'E')
        self.assertEqual(self.rd._substitutions,
                         {'É': 'E', 'Ê': 'E'})

    def test_add_substitions_modify(self):
        self.rd._substitutions = {'$': 'Z'}
        self.rd.add_substitution('$', 'S')
        self.assertEqual(self.rd._substitutions,
                         {'$': 'S'})


CONFIG_SAMPLE = io.StringIO(
    "# Comment"
    "\n"
    "é e\n"
    "À a\n"
    "$ S \n"
    " ï I\n"
    "W vv\n"
)

BROKEN_CONFIG_SAMPLE = io.StringIO(
    "é e\n"
    "À a\n"
    "é\n"
)


class DictoolsTestReader_ConfigSubstitution(unittest.TestCase):
    def setUp(self):
        self.rd = Reader()
        self.rd.dic_path = 'example.yml'
        self.assertEqual(self.rd._substitutions, dict())

    @mock.patch(f'{READER}.add_substitution')
    @mock.patch('builtins.open')
    def test__config_substitions(self, open_mock, add_mock):
        open_mock.return_value = CONFIG_SAMPLE
        self.rd._config_substitutions('cfg.txt')
        calls = [
            mock.call('é', 'e'),
            mock.call('À', 'a'),
            mock.call('$', 'S'),
            mock.call('ï', 'I'),
            mock.call('W', 'vv'),
        ]
        add_mock.assert_called
        self.assertEqual(add_mock.call_args_list, calls)

    @mock.patch(f'{READER}.add_substitution')
    @mock.patch('builtins.open')
    def test_add_substitions_broken(self, open_mock, add_mock):
        open_mock.return_value = BROKEN_CONFIG_SAMPLE
        with self.assertRaises(dictools.ConfigFileException):
            self.rd._config_substitutions('cfg.txt')
            calls = [
                mock.call('é', 'e'),
                mock.call('À', 'a'),
            ]
            self.assertEqual(add_mock.call_args_list, calls)


class DictoolsTestReaderParse(DictoolsTestReaderBasic):
    def test_parse_no_path(self):
        with self.assertRaises(dictools.FileHandlingException):
            self.rd.parse()

    def test_parse_no_filetype(self):
        self.rd.dic_path = 'example.json'
        with self.assertRaises(dictools.FileHandlingException):
            self.rd.parse()

    def test_parse_filetype_different_than_inferred(self):
        self.rd.dic_path = 'example.txt'
        self.rd.filetype = 'application/x-yaml'
        with self.assertRaises(dictools.FileHandlingException):
            self.rd.parse()

    def test_parse_working(self):
        self.rd.dic_path = 'example.txt'
        self.rd.filetype = 'text/plain'
        with mock.patch('motus.dictools.Reader._get_parser') as mock_get:
            self.rd.parse()
            mock_get.assert_called_once_with('text/plain')

    def test_parse_working_2(self):
        self.rd.dic_path = 'example.yml'
        with mock.patch('motus.dictools.Reader._get_parser') as mock_get:
            self.rd.parse()
            mock_get.assert_called_once_with('application/x-yaml')


class DictoolsTestReader_GetParser(DictoolsTestReaderBasic):
    def test__get_parser_txt(self):
        self.assertEqual(
            self.rd._get_parser('text/plain'),
            self.rd._txt_parser
        )

    def test__get_parser_yaml(self):
        self.assertEqual(
            self.rd._get_parser('application/x-yaml'),
            self.rd._yaml_parser
        )

    def test__get_parser_error(self):
        with self.assertRaises(dictools.FileHandlingException):
            self.rd._get_parser('application/json')


# Not really unit tests but the parser involves too many method calls
# for unit testing to be convenient.
class DictoolsTestReader_TxtParser(DictoolsTestReaderBasic):
    def _test__txt_parser(self, file, expected):
        with mock.patch('builtins.open') as mock_open:
            mock_open.return_value = file
            d = self.rd._txt_parser('example.path')
            self.assertEqual(d.content, expected)

    def _test__yaml_parser(self, file, expected):
        with mock.patch('builtins.open') as mock_open:
            mock_open.return_value = file
            d = self.rd._yaml_parser('example.path')
            self.assertEqual(d.content, expected)

    # TXT
    def test__txt_parser_empty(self):
        self._test__txt_parser(
            io.StringIO(''.join(EMPTY_LIST_TXT)),
            {}
        )

    def test__txt_parser_list(self):
        self._test__txt_parser(
            io.StringIO(''.join(LIST_OF_WORDS_TXT)),
            LIST_OF_WORDS
        )

    def test__txt_parser_same_length(self):
        self._test__txt_parser(
            io.StringIO(''.join(DICT_OF_SAME_LENGTH_TXT)),
            DICT_OF_SAME_LENGTH
        )

    def test__txt_parser_full_dic(self):
        self._test__txt_parser(
            io.StringIO(''.join(FULL_DIC_TXT)),
            FULL_DIC
        )

    def test__txt_parser_fake_full_dic(self):
        # The fake Dic is not valid, txt_parser returns only a valid Dic
        # so the values won't be equal
        with self.assertRaises(AssertionError):
            self._test__txt_parser(
                io.StringIO(''.join(FAKE_FULL_DIC_TXT)),
                FAKE_FULL_DIC
            )

    # YAML
    def test__yaml_parser_empty(self):
        self._test__yaml_parser(
            io.StringIO(''.join(EMPTY_LIST_YML)),
            {}
        )

    def test__yaml_parser_list(self):
        self._test__yaml_parser(
            io.StringIO(''.join(LIST_OF_WORDS_YML)),
            LIST_OF_WORDS
        )

    def test__yaml_parser_same_length(self):
        self._test__yaml_parser(
            io.StringIO(''.join(DICT_OF_SAME_LENGTH_YML)),
            DICT_OF_SAME_LENGTH
        )

    def test__yaml_parser_full_dic(self):
        self._test__yaml_parser(
            io.StringIO(''.join(FULL_DIC_YML)),
            FULL_DIC
        )

    def test__yaml_parser_fake_full_dic(self):
        # The yaml parser doens't check the validity of the Dic, maybe an
        # option should be provided
        self._test__yaml_parser(
            io.StringIO(''.join(FAKE_FULL_DIC_YML)),
            FAKE_FULL_DIC
        )


class DictoolsTestReaderClean(DictoolsTestReaderBasic):
    def _test_clean(self, substitutions, word, expected):
        self.rd._substitutions = substitutions
        self.assertEqual(self.rd.clean(word), expected)

    def test_clean_no_subs(self):
        self._test_clean({}, 'APRICOT \n', 'APRICOT')
        self._test_clean({}, '  pear\n', 'PEAR')
        self._test_clean({}, ' BanAna ', 'BANANA')

    def test_clean_subs(self):
        self._test_clean({'À': 'A'}, 'àpricot \n', 'APRICOT')
        self._test_clean({'Ö': 'O'}, '  pear\n', 'PEAR')
        self._test_clean({'A': 'E'}, ' BanAna ', 'BENENE')

    def test_clean_fails(self):
        with self.assertRaises(dictools.NonAplhaWordException):
            self._test_clean({'Ö': 'O'}, 'àpricot \n', 'APRICOT')

        with self.assertRaises(dictools.NonAplhaWordException):
            self._test_clean({'Ö': 'O'}, 'àpricoté \n', 'APRICOT')


class DictoolsTestWriterInstanciation(unittest.TestCase):
    def _test_writer_instanciation(self, *args, **kwargs):
        """`expected`: expected mock.call for Writer.config()"""
        if 'expected' in list(kwargs):
            expected = kwargs.pop('expected')
        else:
            expected = None

        with mock.patch(f'{FILE_HANDLER}.__init__') as fd_mock:
            with mock.patch(f'{WRITER}.config') as cfg_mock:
                rd = Writer(*args, **kwargs)

                self.assertIsInstance(rd, FileHandler)
                self.assertIsInstance(rd, Writer)
                fd_mock.assert_called_once_with()
                cfg_mock.assert_called_once()
                if expected is not None:
                    self.assertEqual(cfg_mock.call_args, expected)

    def test_writer_instanciation_1(self):
        self._test_writer_instanciation(
            expected=mock.call()
        )

    def test_writer_instanciation_2(self):
        self._test_writer_instanciation(
            'path_to_dic',
            expected=mock.call('path_to_dic'),
        )

    def test_writer_instanciation_3(self):
        self._test_writer_instanciation(
            'path_to_dic',
            'filetype',
            expected=mock.call('path_to_dic', 'filetype'),
        )

    def test_writer_instanciation_4(self):
        self._test_writer_instanciation(
            'path/to/dic.txt',
            filetype='text/plain',
            expected=(
                mock.call('path/to/dic.txt',
                          filetype='text/plain',)
            )
        )


class DictoolsTestWriterBasic(unittest.TestCase):
    def setUp(self):
        self.wt = Writer()


class DictoolsTestWriterConfig(DictoolsTestWriterBasic):
    def _test_writer_config(self, *args, **kwargs):
        expected = kwargs.pop('expected')
        """`expected`: expected mock.call for Writer.config()"""
        with mock.patch(f'{FILE_HANDLER}.config') as super_mock:
            self.wt.config(*args, **kwargs)

            super_mock.assert_called_once()
            self.assertEqual(super_mock.call_args, expected)

    def test_writer_config_1(self):
        self._test_writer_config(
            expected=mock.call(None, None)
        )

    def test_writer_config_2(self):
        self._test_writer_config(
            'path_to_dic',
            expected=mock.call('path_to_dic', None),
        )

    def test_writer_config_3(self):
        self._test_writer_config(
            'path_to_dic',
            'filetype',
            expected=mock.call('path_to_dic', 'filetype'),
        )

    def test_writer_config_4(self):
        self._test_writer_config(
            'path/to/dic.txt',
            filetype='text/plain',
            expected=(
                mock.call('path/to/dic.txt',
                          'text/plain',)
            )
        )


class DictoolsTestWriterParse(DictoolsTestWriterBasic):
    def setUp(self):
        super().setUp()
        self.dic = dictools.Dic()

    def test_write_no_path(self):
        with self.assertRaises(dictools.FileHandlingException):
            self.wt.write(self.dic)

    def test_write_no_filetype(self):
        self.wt.dic_path = 'example'
        with self.assertRaises(dictools.FileHandlingException):
            self.wt.write(self.dic)

    def test_write_filetype_different_than_inferred(self):
        self.wt.dic_path = 'example.txt'
        self.wt.filetype = 'application/x-yaml'
        with self.assertRaises(dictools.FileHandlingException):
            self.wt.write(self.dic)

    def test_write_working(self):
        self.wt.dic_path = 'example.txt'
        self.wt.filetype = 'text/plain'
        with mock.patch('motus.dictools.Writer._get_writer') as mock_get:
            self.wt.write(self.dic)
            mock_get.assert_called_once_with('text/plain')

    def test_write_working_2(self):
        self.wt.dic_path = 'example.yml'
        with mock.patch('motus.dictools.Writer._get_writer') as mock_get:
            self.wt.write(self.dic)
            mock_get.assert_called_once_with('application/x-yaml')


class DictoolsTestWriter_GetParser(DictoolsTestWriterBasic):
    def test__get_writer_txt(self):
        self.assertEqual(
            self.wt._get_writer('text/plain'),
            self.wt._txt_writer
        )

    def test__get_writer_yaml(self):
        self.assertEqual(
            self.wt._get_writer('application/x-yaml'),
            self.wt._yaml_writer
        )

    def test__get_writer_error(self):
        with self.assertRaises(dictools.FileHandlingException):
            self.wt._get_writer('application/json')


class TestDictoolsWriterWrite(DictoolsTestWriterBasic):
    def setUp(self):
        super().setUp()
        self.dic = dictools.Dic()

        tmp_handler, tmp_path = tempfile.mkstemp()
        self.tmp_handler = tmp_handler
        self.tmp_path = tmp_path

        self.tmp_file = open(tmp_path, 'r')

    def tearDown(self):
        self.tmp_file.close()
        os.close(self.tmp_handler)


class TestDictoolsWriterWriteYaml(TestDictoolsWriterWrite):
    def _test_write_yaml(self, filetype, content, expected_file):
        self.dic.content = content
        self.wt.config(self.tmp_path, filetype)

        self.wt._yaml_writer(self.dic, self.tmp_path)

        self.assertEqual(
            self.tmp_file.readlines(),
            expected_file,
        )

    def test_write_yaml_empty(self):
        self._test_write_yaml(
            'application/x-yaml',
            EMPTY_LIST,
            ['[]\n']
        )

    def test_write_yaml_list(self):
        self._test_write_yaml(
            'application/x-yaml',
            LIST_OF_WORDS,
            LIST_OF_WORDS_YML
        )

    def test_write_yaml_same_length(self):
        self._test_write_yaml(
            'application/x-yaml',
            DICT_OF_SAME_LENGTH,
            DICT_OF_SAME_LENGTH_YML
        )

    def test_write_yaml_full_dic(self):
        self._test_write_yaml(
            'application/x-yaml',
            FULL_DIC,
            FULL_DIC_YML
        )


class TestDictoolsWriterWriteTxt(TestDictoolsWriterWrite):
    def _test_write_txt(self, filetype, content, expected_file):
        self.dic.content = content

        self.wt._txt_writer(self.dic, self.tmp_path)

        self.assertEqual(
            self.tmp_file.readlines(),
            expected_file,
        )

    def test_write_txt_empty(self):
        self._test_write_txt(
            'text/plain',
            EMPTY_LIST,
            []
        )

    def test_write_txt_list(self):
        self._test_write_txt(
            'text/plain',
            LIST_OF_WORDS,
            LIST_OF_WORDS_TXT
        )

    def test_write_txt_same_length(self):
        self._test_write_txt(
            'text/plain',
            DICT_OF_SAME_LENGTH,
            DICT_OF_SAME_LENGTH_TXT
        )

    def test_write_txt_full_dic(self):
        self._test_write_txt(
            'text/plain',
            FULL_DIC, 
            FULL_DIC_TXT
        )


if __name__ == '__main__':
    unittest.main()
