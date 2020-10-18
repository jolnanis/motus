from abc import ABC, abstractmethod
from collections import Counter
import random

from motus import dictools, player
from motus.ui import UI


DEFAULT_MINLENGTH = 5
DEFAULT_MAXLENGTH = 12
DEFAULT_GUESSES = 12


class Game(ABC):
    def __init__(self, filename, filetype, pckg):
        self.load_dic(filename, filetype, pckg)
        super().__init__()

    def load_dic(self, filename, filetype, pckg):
        """Returns the content of a dictionary given its filename"""
        rd = dictools.Reader()
        rd.config(filename, filetype, None, pckg)
        self.dic = rd.parse()

    @abstractmethod
    def play(self):
        pass


class SoloGame(Game):
    def __init__(self, filename, filetype=None, pckg=True):
        self.wins = 0
        self.rounds = 0
        self.player = player.HumanPlayer()
        super().__init__(filename, filetype, pckg)

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
        all_words = self.game.dic.content[self.wordlength]

        first_letter = random.choice(list(all_words))
        self.solution = random.choice(list(all_words[first_letter]))

    def evaluate(self, guess):
        return evaluate(self.solution, guess)


class SoloRound(Round):
    def play(self):
        self.game.incr_rounds()

        UI.init_round(self.wordlength)
        UI.display_first_word(self.solution[0])

        for i in range(DEFAULT_GUESSES):
            guess = self.game.player.guess()

            res, hints = self.evaluate(guess)
            UI.display_correction(guess, hints)

            if res:
                self.game.incr_wins()
                UI.right_guess(self.solution)
                break

        if not res:
            UI.display_solution(self.solution)


def evaluate(solution, guess):
    """ Returns a tuple of a boolean and a hint string.

    The boolean is `True` iff the guessed word is the solution

    Hint string encoding, for each letter:\n
    `R` Right : Good letter in the good place.\n
    `M` Misplaced : Good letter in a bad place.\n
    `W` Wrong : Letter used too many times"""
    wordlength = len(solution)

    # Obvious cases handling :
    if len(guess) != wordlength or guess[0] != solution[0]:
        return False, 'W' * wordlength

    if guess == solution:
        return True, 'R' * wordlength

    # Other cases, initialize with "all wrong" hint list
    hints = ['W'] * wordlength

    # First pass: fill-up right guesses
    letters = Counter(solution)
    for i in range(len(solution)):
        right_letter = solution[i]
        guessed_letter = guess[i]
        if guessed_letter == right_letter:
            hints[i] = 'R'
            letters[guessed_letter] = letters[guessed_letter] - 1

    # Second pass: fill-up misplaced guesses
    for i in range(len(solution)):
        right_letter = solution[i]
        guessed_letter = guess[i]

        if hints[i] == 'R':
            continue

        if guessed_letter in list(letters) and letters[guessed_letter] > 0:
            hints[i] = 'M'
            letters[guessed_letter] = letters[guessed_letter] - 1

    hints = ''.join(hints)  # Convert hint list to hint string
    return False, hints


def main():
    game = SoloGame('wordlist_fr.yml')
    game.play()


if __name__ == "__main__":

    main()
