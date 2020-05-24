from collections import Counter
import re
import unittest
from unittest import mock

from colorama import Fore, Style

from motus.ui import UI


class UITestSelectWordlength(unittest.TestCase):
    def _test_select_wordlength(self, bounds, mocked_input, expected_res):
        with mock.patch('builtins.input', side_effect=mocked_input):
            res = UI.select_wordlength(bounds[0], bounds[1])
            self.assertEqual(res, expected_res)

    def test_select_wordlength_basic(self):
        self._test_select_wordlength([7, 12], ['8'], 8)

    def test_select_wordlength_change_bounds(self):
        self._test_select_wordlength([1, 6], ['5'], 5)

    def test_select_wordlength_extended(self):
        self._test_select_wordlength([7, 12], ['99', 'w', '!', ' ', '9'], 9)

    def test_select_wordlength_long_input(self):
        self._test_select_wordlength([7, 12],
                                     ['99', 'w', '!', ' ', '10', '11'], 10)


class UITestPrompt(unittest.TestCase):
    def _test_prompt_basic(self, fun, mocked_input, expected_res):

        with mock.patch('builtins.input', side_effect=mocked_input):
            res = fun()
            self.assertEqual(res, expected_res)


class UITestPromptGuess(UITestPrompt):
    def test_prompt_guess(self):
        self._test_prompt_basic(UI.prompt_guess, ['bateau'], 'BATEAU')
        self._test_prompt_basic(UI.prompt_guess, [' Avion'], 'AVION')
        self._test_prompt_basic(UI.prompt_guess, ['MANGER  '], 'MANGER')
        self._test_prompt_basic(UI.prompt_guess, ['BANG BANG'], 'BANG BANG')
        self._test_prompt_basic(UI.prompt_guess, ['!'], '!')
        self._test_prompt_basic(UI.prompt_guess, [''], '')


class UITestAskReplay(UITestPrompt):
    def test_ask_replay_yes(self):
        self._test_prompt_basic(UI.ask_replay, ['yes'], True)
        self._test_prompt_basic(UI.ask_replay, ['Yes'], True)
        self._test_prompt_basic(UI.ask_replay, ['yeS'], True)
        self._test_prompt_basic(UI.ask_replay, ['YES'], True)
        self._test_prompt_basic(UI.ask_replay, ['y'], True)
        self._test_prompt_basic(UI.ask_replay, ['Y'], True)

    def test_ask_replay_no(self):
        self._test_prompt_basic(UI.ask_replay, ['n'], False)
        self._test_prompt_basic(UI.ask_replay, ['N'], False)
        self._test_prompt_basic(UI.ask_replay, ['no'], False)
        self._test_prompt_basic(UI.ask_replay, ['NO'], False)
        self._test_prompt_basic(UI.ask_replay, ['No'], False)

    def test_ask_replay_ambiguous(self):
        self._test_prompt_basic(UI.ask_replay, [''], False)
        self._test_prompt_basic(UI.ask_replay, ['\n'], False)
        self._test_prompt_basic(UI.ask_replay, ['$'], False)
        self._test_prompt_basic(UI.ask_replay, ['maybe'], False)


class UITestInitRound(unittest.TestCase):
    def _test_init_round(self, wordlength):
        UI.init_round(wordlength)
        self.assertIsNotNone(UI.wordlength)
        self.assertEqual(UI.wordlength, wordlength)

    def test_init_round(self):
        self._test_init_round(12)
        self._test_init_round(8)
        self._test_init_round(5)
        self._test_init_round(1)


class UITestDisplay(unittest.TestCase):

    ALL_FORES = [Fore.__getattribute__(attr) for attr in dir(Fore)
                 if attr[0].isalpha()]
    ALL_STYLES = [Style.__getattribute__(attr) for attr in dir(Style)
                  if attr[0].isalpha()]
    ALL_MODS = ALL_FORES + ALL_STYLES

    def _to_regex(self, lst):
        return str.join('|', [re.escape(elem) for elem in lst])

    def _extract_message(self, mock_print):
        mock_print.assert_called_once()
        name, args, kwargs = mock_print.mock_calls[0]
        message = args[0]
        return message

    def _no_mods(self, message):
        r_mods = self._to_regex(self.ALL_MODS)
        return re.sub(r_mods, '', message)

    def _style_only(self, message):
        r_styles = self._to_regex(self.ALL_STYLES)
        return str.join('', re.findall(r_styles, message))

    def _fore_only(self, message):
        r_fores = self._to_regex(self.ALL_FORES)
        return str.join('', re.findall(r_fores, message))

    def _test_display_basic(self, fun, *args, **kwargs):
        if 'expected_res' in list(kwargs):
            expected_res = kwargs.pop('expected_res')
        else:
            raise Exception("_test_display_basic needs an 'expected_res' kwarg")

        with mock.patch('builtins.print') as mock_print:
            fun(*args, **kwargs)
            message = self._extract_message(mock_print)

            self.assertEqual(message, expected_res)


class UITestDisplayFirstWord(UITestDisplay):
    def _test_display_first_word(self, wordlength, first_letter):
        UI.wordlength = wordlength

        with mock.patch('builtins.print') as mock_print:
            UI.display_first_word(first_letter)

            message = self._extract_message(mock_print)
            self.assertEqual(len(message), wordlength * 3)

            letters = Counter(message)

            self.assertEqual(message[1], first_letter)
            self.assertIn(first_letter, list(letters))
            self.assertEqual(letters[first_letter], 1)

            self.assertIn('-', list(letters))
            self.assertEqual(letters['-'], wordlength - 1)

    def test_display_first_word(self):
        self._test_display_first_word(3, 'A')
        self._test_display_first_word(12, 'W')
        self._test_display_first_word(7, 'X')


class UITest_DisplayLetter(UITestDisplay):
    # /!\ Method namespace broken for legibility
    def _test_printed_no_mods(self, letter, hint, expected_naked_message):
        with mock.patch('builtins.print') as mock_print:
            UI._display_letter(letter, hint)

            message = self._extract_message(mock_print)
            naked_message = self._no_mods(message)

            self.assertEqual(naked_message, expected_naked_message)

    # /!\ Method namespace broken for legibility
    def _test_printed_style(self, letter, hint, expected_style):
        with mock.patch('builtins.print') as mock_print:
            UI._display_letter(letter, hint)

            message = self._extract_message(mock_print)
            mod_section = message[:-3]
            style = self._style_only(mod_section)

            self.assertEqual(len(style), len(expected_style))
            self.assertEqual(style, expected_style)

    # /!\ Method namespace broken for legibility
    def _test_printed_fore(self, letter, hint, expected_fore):
        with mock.patch('builtins.print') as mock_print:
            UI._display_letter(letter, hint)

            message = self._extract_message(mock_print)
            mod_section = message[:-3]
            fore = self._fore_only(mod_section)

            self.assertEqual(len(fore), len(expected_fore))
            self.assertEqual(fore, expected_fore)

    # Double underscore to respect namespace
    def test__display_letter_no_mods(self):
        self._test_printed_no_mods('A', 'R', '[A]')
        self._test_printed_no_mods('X', 'W', ' X ')
        self._test_printed_no_mods('B', 'M', '(B)')
        self._test_printed_no_mods('W', 'W', ' W ')
        self._test_printed_no_mods('N', 'R', '[N]')

    # Double underscore to respect namespace
    def test__display_letter_style(self):
        self._test_printed_style('A', 'R', Style.BRIGHT)
        self._test_printed_style('X', 'W', '')
        self._test_printed_style('B', 'M', Style.BRIGHT)
        self._test_printed_style('W', 'W', '')
        self._test_printed_style('N', 'R', Style.BRIGHT)

    # Double underscore to respect namespace
    def test__display_letter_fore(self):
        self._test_printed_fore('A', 'R', Fore.RED)
        self._test_printed_fore('X', 'W', '')
        self._test_printed_fore('B', 'M', Fore.YELLOW)
        self._test_printed_fore('W', 'W', '')
        self._test_printed_fore('N', 'R', Fore.RED)

    def test__display_letter_error(self):
        with self.assertRaises(TypeError):
            UI._display_letter('B', '')

        with self.assertRaises(TypeError):
            UI._display_letter('G', 'A')


class UITestDisplaySolution(UITestDisplay):
    def test_display_solution_short(self):
        self._test_display_basic(
            UI.display_solution, 'OUI',
            expected_res="Sorry, the right answer was: OUI"
        )

    def test_display_solution_long(self):
        self._test_display_basic(
            UI.display_solution, 'MOUCHERON',
            expected_res="Sorry, the right answer was: MOUCHERON"
        )

    def test_display_solution_empty(self):
        self._test_display_basic(
            UI.display_solution, '',
            expected_res="Sorry, the right answer was: "
        )


class UITestRightGuess(UITestDisplay):
    def test_right_guess_short(self):
        self._test_display_basic(
            UI.right_guess, 'OUI',
            expected_res="Congratulations, OUI was the right answer !"
        )

    def test_right_guess_long(self):
        self._test_display_basic(
            UI.right_guess, 'MOUCHERON',
            expected_res="Congratulations, MOUCHERON was the right answer !"
        )

    def test_right_guess_empty(self):
        self._test_display_basic(
            UI.right_guess, '',
            expected_res="Congratulations,  was the right answer !"
        )


class UITestDisplayScoreSolo(UITestDisplay):
    def test_display_score_solo(self):
        self._test_display_basic(
            UI.display_score_solo, 0, 10,
            expected_res="You have 0 wins over 10 rounds."
        )

        self._test_display_basic(
            UI.display_score_solo, 8, 8,
            expected_res="You have 8 wins over 8 rounds."
        )


class UITestDisplayCorrection(unittest.TestCase):
    def _extract_args(self, mock_call):
        args, kwargs = mock_call
        return args

    def _extract_args_list(self, mock_disp):
        return [self._extract_args(mock_call) for mock_call
                in mock_disp.call_args_list]

    def _test_display_correction(self, guess, correction, expected_res):
        with mock.patch('motus.ui.UI._display_letter') as mock_disp:
            UI.display_correction(guess, correction)

            res = self._extract_args_list(mock_disp)
            self.assertEqual(res, expected_res)

    def test_display_correction_correct(self):
        UI.wordlength = 7
        self._test_display_correction(
            'CORRECT', 'RRRRRRR',
            [
                ('C', 'R'),
                ('O', 'R'),
                ('R', 'R'),
                ('R', 'R'),
                ('E', 'R'),
                ('C', 'R'),
                ('T', 'R'),
            ]
        )

    def test_display_correction_wrong(self):
        UI.wordlength = 5
        self._test_display_correction(
            'WRONG', 'WWWWW',
            [
                ('W', 'W'),
                ('R', 'W'),
                ('O', 'W'),
                ('N', 'W'),
                ('G', 'W'),
            ]
        )

    def test_display_correction_incorrect(self):
        UI.wordlength = 9
        self._test_display_correction(
            'INCORRECT', 'RRWWMMWWR',
            [
                ('I', 'R'),
                ('N', 'R'),
                ('C', 'W'),
                ('O', 'W'),
                ('R', 'M'),
                ('R', 'M'),
                ('E', 'W'),
                ('C', 'W'),
                ('T', 'R'),
            ]
        )

    def test_display_correction_incomplete(self):
        UI.wordlength = 10
        self._test_display_correction(
            'INCOMPL', 'WWWWWWWWWW',
            [
                ('I', 'W'),
                ('N', 'W'),
                ('C', 'W'),
                ('O', 'W'),
                ('M', 'W'),
                ('P', 'W'),
                ('L', 'W'),
                ('-', 'W'),
                ('-', 'W'),
                ('-', 'W'),
            ]
        )


if __name__ == '__main__':
    unittest.main()
