from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator


def is_valid(option):
    return option == str(1) or option == str(2) or option == "."


def create_menu(title, choices, cancel="import", completer=None, validate_method=None):
    """
    A basic function which creates a menu with title and choices.

    :param cancel:
    :param title: Heading text
    :type title: String
    :param choices: Options to choose
    :type choices: List of strings
    :param completer: Optional argument that shows possible options while typing.
    :type completer: :class:`prompt_toolkit.completion.FuzzyWordCompleter`
    :param validate_method: Possible validator function
    :type validate_method: Function
    :return: Entered choice
    :rtype: String
    """
    validator = None
    if validate_method is not None:
        validator = Validator.from_callable(
            validate_method,
            error_message="You didn't select a valid option",
            move_cursor_to_end=True,
        )

    input_text = title + "\n"
    for index, choice in enumerate(choices, 1):
        input_text += f"   {str(index)}) {choice}\n"
    input_text += f"   .) Cancel {cancel}\n > "
    choice = prompt(input_text, completer=completer, validator=validator)

    return choice
