import warnings
import yaml


class SubFileException(Exception):
    """Exception raised when Substitution file is poorly formed"""


class NonAplhaWordWarning(Warning):
    """Raised when a word is not composed of A-Z letters"""


class WordSet:
    """Toolbox class used to manipulate, clean and save word sets. \n
    Words are cleaned automatically upon addition to the set.
    """

    def __init__(self, import_file=None, substitution_file=None):
        self._content = set()
        self._substitutions = {}

        if substitution_file is not None:
            self.read_substitutions(substitution_file)

        if import_file is not None:
            self.read(import_file)

    def add_substitution(self, old, new):
        self._substitutions[old.upper()] = new.upper()

    def read_substitutions(self, path):
        i = 0
        for line in open(path, 'r'):
            i = i+1
            line = line.strip()
            if line == '' or line[0] == '#':
                continue

            try:
                old, new = line.split(' ')
                self.add_substitution(old, new)

            except ValueError as e:
                raise SubFileException(
                    f'Could not parse line {i} of file {path}:\n'
                    f'{line}'
                ) from e

    def add(self, word):
        """Cleans a word and adds it to the WordSet"""
        word = word.strip()
        word = word.upper()
        for old, new in self._substitutions.items():
            word = word.replace(old, new)

        if (word.isascii() and word.isalpha()):
            self._content.add(word)
        else:
            warnings.warn(NonAplhaWordWarning(
                f'Word {word} not composed of A-Z letters: ignored'
            ))

    def read(self, path):
        for line in open(path, 'r'):
            self.add(line)

    def write_list(self, path):
        word_list = sorted(self._content)

        file = open(path, 'w')
        for word in word_list:
            file.write(word + '\n')
        file.close()

    def write_dict(self, path):
        word_list = sorted(self._content)

        d = {}
        for word in word_list:
            if len(word) not in list(d):
                d[len(word)] = {}
            if word[0] not in d[len(word)]:
                d[len(word)][word[0]] = []
            d[len(word)][word[0]].append(word)

        file = open(path, 'w')
        yaml.dump(d, file)
        file.close()
