import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)


class UI:
    @classmethod
    def select_wordlength(cls, minlength, maxlength):
        while True:
            wordlength = input("Select a word length: ")

            if (wordlength.isnumeric() and int(wordlength) > minlength - 1
                    and int(wordlength) < maxlength + 1):

                return int(wordlength)
                continue

            else:
                print(f'Please select a valid  number '
                      f'in range ({minlength}-{maxlength})')

    @classmethod
    def ask_replay(cls):
        answer = input("Replay ? (y/N) ")
        return answer.upper() in ['Y', 'YES']

    @classmethod
    def init_round(cls, wordlength):
        cls.wordlength = wordlength

    @classmethod
    def display_first_word(cls, first_letter):
        fill = cls.wordlength - 1
        output = f' {first_letter} ' + ' - ' * fill
        print(output)

    @classmethod
    def prompt_guess(cls):
        guess = input('> ')
        clean_guess = guess.upper().strip()
        return clean_guess

    @classmethod
    def right_guess(cls, solution):
        print(f'Congratulations, {solution} was the right answer !')

    @classmethod
    def display_correction(cls, guess, hints):
        adjusted_guess = guess.ljust(cls.wordlength, '-')[:cls.wordlength]

        for letter, hint in zip(adjusted_guess, hints):
            cls._display_letter(letter, hint)
        print()

    @classmethod
    def _display_letter(cls, letter, hint):
        if hint == 'R':
            print(Fore.RED + Style.BRIGHT + f'[{letter}]', end='')
        elif hint == 'M':
            print(Fore.YELLOW + Style.BRIGHT + f'({letter})', end='')
        elif hint == 'W':
            print(f' {letter} ', end='')
        else:
            raise TypeError

    @classmethod
    def display_solution(cls, solution):
        """ Called when the player has exceeded their number of guesses. \n
        Displays the solution along with a kind word."""

        print(f'Sorry, the right answer was: {solution}')

    @classmethod
    def display_score_solo(cls, wins, rounds):
        print(f'You have {wins} wins over {rounds} rounds.')
