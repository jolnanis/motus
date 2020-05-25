from abc import ABC, abstractmethod
from collections import Counter
import pkgutil
import random
import yaml

from motus.ui import UI


DEFAULT_MINLENGTH = 5
DEFAULT_MAXLENGTH = 12
DEFAULT_GUESSES = 12


class Game(ABC):
    def __init__(self, dico_filename):
        self.load_dico(dico_filename)
        super().__init__()

    def load_dico(self, filename):
        """Returns the content of a dictionary given its filename"""
        try:
            data = pkgutil.get_data('motus.dic', filename)
            self.dico = yaml.safe_load(data.decode())
        except FileNotFoundError:
            raise

    @abstractmethod
    def play(self):
        pass


class SoloGame(Game):
    def __init__(self, dico_filename):
        self.wins = 0
        self.rounds = 0
        super().__init__(dico_filename)

    def incr_wins(self):
        self.wins = self.wins+1

    def incr_rounds(self):
        self.rounds = self.rounds+1

    def play(self):
        wordlength = UI.select_wordlength(DEFAULT_MINLENGTH, DEFAULT_MAXLENGTH)

        replay = True
        while replay:
            rd = SoloRound(self, wordlength)
            rd.play()
            UI.display_score_solo(self.wins, self.rounds)
            replay = UI.ask_replay()


class Round(ABC):
    def __init__(self, game, wordlength):
        self.game = game
        self.wordlength = wordlength
        self.pick_solution()
        super().__init__()

    @abstractmethod
    def play(self):
        pass

    def pick_solution(self):
        all_words = self.game.dico[self.wordlength]

        first_letter = random.choice(list(all_words))
        self.solution = random.choice(list(all_words[first_letter]))

    def evaluate(self, guess):
        """ Returns a tuple of a boolean and a correction string.

        The boolean is `True` if the guessed word is the solution

        The correction string is the same length as the solution and contains:\n
        `R` Right : Good letter in the good place.\n
        `M` Misplaced : Good letter in a bad place.\n
        `W` Wrong : Letter used too many times"""
        if len(guess) != self.wordlength:
            return False, 'W' * self.wordlength

        solution = self.solution
        letters = Counter(solution)

        if guess == solution:
            return True, 'R' * self.wordlength

        correction = ''
        for correct_letter, guessed_letter in zip(solution, guess):

            if correct_letter == guessed_letter:
                correction = correction + 'R'
                letters[correct_letter] = letters[correct_letter] - 1

            elif guessed_letter in list(letters) and letters[guessed_letter] > 0:
                correction = correction + 'M'
                letters[guessed_letter] = letters[guessed_letter] - 1

            else:
                correction = correction + 'W'

        return False, correction


class SoloRound(Round):
    def play(self):
        self.game.incr_rounds()

        UI.init_round(self.wordlength)
        UI.display_first_word(self.solution[0])

        for i in range(DEFAULT_GUESSES):
            guess = UI.prompt_guess()

            res, correction = self.evaluate(guess)
            UI.display_correction(guess, correction)

            if res:
                self.game.incr_wins()
                UI.right_guess(self.solution)
                break

        if not res:
            UI.display_solution(self.solution)


def main():
    game = SoloGame('wordlist_fr.yml')
    game.play()


if __name__ == "__main__":

    main()
