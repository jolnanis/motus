from abc import ABC, abstractmethod
import gc
import mimetypes
import pkgutil

import yaml

import motus

class FileHandlingException(Exception):
    """Exception raised during opening a dic file for Read/Write operations"""


class ParsingException(FileHandlingException):
    """Exception raised durin parsing"""


class NonAplhaWordException(ParsingException):
    """Raised when a word is not composed of A-Z letters"""

class ConfigFileException(Exception):
    """Exception raised when Substitution file is poorly formed"""


class DicStateException(Exception):
    """Exception raised when encountering a"""


def new_dic(*args, **kwargs):
    if 'dic_path' in list(kwargs) or args != ():
        rd = Reader()
        rd.config(*args, **kwargs)
        return rd
    else:
        return Dic()


class Dic:
    """Toolbox class used to manipulate, clean and save word sets. \n
    Words are cleaned automatically upon addition to the set.
    """
    def __init__(self):
        self.content = dict()
        self._state_flag = True
        self._words_flag = True

    @property
    def state(self):
        if self._state_flag or self._state is None:
            if self.content == {} or self.content == []:
                self._state = 'empty'
            elif isinstance(self.content, list):
                self._state = 'list of words'
            elif isinstance(list(self.content)[0], str):
                self._state = 'various-initials dict'
            elif isinstance(self.content, dict):
                self._state = 'various-lengths dict'
            else:
                raise Exception('Internal Dictionnary corrupted')
            self._state_flag = False

        return self._state

    @property
    def words(self):
        if self._words_flag or self._words is None:
            content = self.content
            if self.state == 'various-lengths dict':
                self._words = [
                    word for length in list(content)
                    for initial in list(content[length])
                    for word in content[length][initial]
                ]
            elif self.state == 'various-initials dict':
                self._words = [
                    word for initial in list(content)
                    for word in content[initial]
                ]
            elif self.state == 'list of words':
                self._words = content
            elif self.state == 'empty':
                self._words = []

            self._words_flag = False

        return self._words

    def _insert(self, word, container, state):
        self._state_flag = True
        if state == 'empty':
            return [word]
        elif state == 'list of words':
            if len(word) == len(container[0]):
                if container == [] or word[0] == container[0][0]:
                    container.append(word)
                    return container
                else:
                    return {word[0]: [word], container[0][0]: container}
            else:
                return {
                    len(word): {word[0]: [word]}, 
                    len(container[0]): {container[0][0]: container},
                }
        elif state == 'various-initials dict':
            one_word = container[list(container)[0]][0]
            if len(word) == len(one_word):
                if word[0] in list(container):
                    container[word[0]].append(word)
                    return container
                else:
                    container[word[0]] = [word]
                    return container
            else:
                return {
                    len(word): {word[0]: [word]}, 
                    len(one_word): container
                }
        elif state == 'various-lengths dict':
            if len(word) in list(container):
                container[len(word)] = self._insert(
                    word,
                    container[len(word)],
                    'various-initials dict',
                )
                return container
            else:
                container[len(word)] = {word[0]: [word]}
                return container


    def insert(self, word):
        if word is None:
            return
        try:
            self.content = self._insert(word, self.content, self.state)
        except KeyError:
            err_str = ('Problem when adding an entry to the dic. '
                       'Internal state corrupted')
            raise DicStateException(err_str)
            


class FileHandler(ABC):
    """ Parent abstract class for dictools.Reader and dictools.Writer
    """
    if mimetypes.guess_type('example.yml')[0] is None:
        mimetypes.add_type('application/x-yaml', '.yml')
        mimetypes.add_type('application/x-yaml', '.yaml')

    @abstractmethod
    def __init__(self):
        self.dic_path = None
        self.filetype = None
        self._infer_flag = True

    def config(self, dic_path, filetype):
        if dic_path is not None:
            self.dic_path = dic_path
            self._infer_flag = True
        if filetype is not None:
            self.filetype = filetype

    @property
    def inferred_filetype(self):
        if self._infer_flag or self._inferred_filetype is not None:
            if self.dic_path is not None:
                self._inferred_filetype = mimetypes.guess_type(self.dic_path)[0]
                self._infer_flag = False

        return self._inferred_filetype


class Reader(FileHandler):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.pckg = None
        self._substitutions = {}
        self.config(*args, **kwargs)

    def config(self, dic_path=None, filetype=None, config=None, pckg=None):
        """Takes up to 4 positional keyword arguments :\n
        `dic_path`: str, path to the dictionary\n
        `filetype`: str, accepts `text/plain` and `application/x-yaml`\n
        `config`: str, path to a config file\n
        `pckg`: bool, `True` if the dic should be retrieved from the package
        """
        if pckg is not None:
            self.pckg = pckg
        if config is not None:
            self._config_substitutions(config)
        super().config(dic_path, filetype)

    def add_substitution(self, old: str, new: str):
        print(self._substitutions)
        self._substitutions[old.upper()] = new.upper()

    def _config_substitutions(self, config_file):
        self._substitutions = dict()
        with open(config_file, 'r') as file:
            i = 0
            for line in file:
                i = i+1
                line = line.strip()
                if line == '' or line[0] == '#':
                    continue

                try:
                    old, new = line.split(' ')
                    self.add_substitution(old, new)

                except ValueError as e:
                    raise ConfigFileException(
                        f'Could not parse line {i} of file {self.dic_path}:\n'
                        f'{line}'
                    ) from e

    def parse(self, dic_path=None, filetype=None, pckg=None):
        if (dic_path or filetype or pckg) is not None:
            self.config(dic_path=dic_path, filetype=filetype, pckg=pckg)

        if 'dic_path' not in dir(self) or self.dic_path is None:
            raise FileHandlingException('No Target file')

        if (('filetype' not in dir(self) or self.filetype is None)
                and self.inferred_filetype is None):
            raise FileHandlingException(f'Could not infer a file type for'
                                        f'{self.file_path}')

        if ((self.filetype and self.inferred_filetype) is not None 
            and self.filetype != self.inferred_filetype):
            err_str = (f'Incompatible filetypes: {self.filetype}, '
                       f'{self.inferred_filetype}')
            raise FileHandlingException(err_str)

        return self._get_parser(self.filetype or self.inferred_filetype)

    def _get_parser(self, filetype):
        if filetype == 'text/plain':
            return self._txt_parser(self.dic_path)
        elif filetype == 'application/x-yaml':
            return self._yaml_parser(self.dic_path)
        else:
            raise FileHandlingException('Unknown filetype: {filetype}')

    def _txt_parser(self, path):
        d = new_dic()
        for line in open(path, 'r'):
            d.insert(self.clean(line))

        return d

    def _yaml_parser(self, path):
        d = new_dic()
        if self.pckg:
            data = pkgutil.get_data('motus.dic', self.dic_path)
            d.content = yaml.safe_load(data.decode())
            del data
            gc.collect()
        else:
            with open(path, 'r') as file:
                d.content = yaml.safe_load(file)

        if d.content is None:
            d.content = {}

        return d

    def clean(self, line):
        word = line.strip().upper()
        for old, new in self._substitutions.items():
            word = word.replace(old, new)

        if word == '':
            return None

        if (ord(min(word)) > 64 and ord(max(word)) < 90):
            return word

        else:
            unauth = [char for char in word if ord(char) < 64 or ord(char) > 90]
            if len(unauth) == 1:
                error_str = f'Unauthorized character {unauth[0]} in word {word}'
            else:
                error_str = f'Unauthorized characters {unauth} in word {word}'
            raise NonAplhaWordException(error_str)


class Writer(FileHandler):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.config(*args, **kwargs)

    def config(self, dic_path=None, filetype=None):
        """ Takes up to 2 positionnal keywoard arguments :\n
        `dic_path`: str, path to the dictionary being written\n
        `filetype`: str, accepts `text/plain` and `application/x-yaml`
        """
        super().config(dic_path, filetype)

    def write(self, dic, dic_path=None, filetype=None):
        if (dic_path or filetype is not None):
            self.config(dic_path, filetype)

        if 'dic_path' not in dir(self) or self.dic_path is None:
            raise FileHandlingException('No Destination file')

        if (('filetype' not in dir(self) or self.filetype is None)
                and self.inferred_filetype is None):
            raise FileHandlingException(f'Could not infer a file type for'
                                        f'{self.dic_path}')

        if ((self.filetype and self.inferred_filetype) is not None 
            and self.filetype != self.inferred_filetype):
            err_str = (f'Incompatible filetypes: {self.filetype}, '
                       f'{self.inferred_filetype}')
            raise FileHandlingException(err_str)

        return self._get_writer(self.filetype or self.inferred_filetype)

    @classmethod
    def _get_writer(cls, filetype):
        if filetype == 'text/plain':
            return cls._txt_writer
        elif filetype == 'application/x-yaml':
            return cls._yaml_writer
        else:
            raise FileHandlingException('Unknown filetype: {filetype}')

    @classmethod
    def _txt_writer(cls, dic, path):
        try:
            file = open(path, 'w')
            open_flag = True
            for word in dic.words:
                file.write(word + '\n')
            file.close()
            open_flag = False
        except Exception:
            if open_flag:
                file.close()
            raise

    @classmethod
    def _yaml_writer(cls, dic, path):
        try:
            file = open(path, 'w')
            open_flag = True
            yaml.dump(dic.content, file, default_flow_style=False)
            file.close()
            open_flag = False
        except Exception:
            if open_flag:
                file.close()
            raise
