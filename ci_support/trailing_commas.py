#!/usr/bin/env python3
"""
Credit to groboclown for original work.  Original source gist is
[here](https://gist.github.com/groboclown/a548643d649cb06c04ed7e4b4121f339).

Modifications to fit this project added following commit e276e02.

---

An extension to PyLint.  It enforces a coding style similar to Golang in
regards to multi-line list expressions.

To add it to your run of PyLint, add the file's directory to your
`PYTHONPATH` environment variable, and run:

```bash
python3 -m pylint \
    --load-plugins trailing_commas \
    my_packages to_lint
```

It encourages a coding style like:

```python
def my_func(
        arg_1,
        arg_2,
):
    # Lists, tuples, dictionaries, sets, and function arguments, if multi-line,
    # need to include a comma after the last item.
    x = [
        "a",
        "b-c",
        "d-e-f",
    ]
    # list constructor expressions are recognized and don't need a comma.
    y = [
        v.upper()
        for value in x
    ]
    if (
        # if, elif, and other multi-line statements that aren't lists are
        # identified as such, and don't need a trailing comma
        len(arg_1) > 1 and
        len(arg_2) < 10
    ):
        return x
    # Returning items on the same line is fine, and you can use the option
    # 'comma-always-after-last-tuple' to require tuples to have a final
    # comma.
    return (len(x), len(y), "string-value",)
```

This has two options that can be set:

    _ 'comma-always-after-last-tuple' : set to "y" or "n".  If set, then
        a comma is always required after the last item in a tuple, regardless
        of whether it is multi-line or not.  The linter makes a best effort
        to discover whether a parenthetical expression is a tuple or not.
    _ 'one-item-per-line' : set to "y" or "n".  If set, then the extension
        reports a problem if a multi-line list has more than one item on a
        line.

This was made as part of the Petronia project.
"""

from typing import List, Tuple, Sequence, Optional
import tokenize
import pylint.lint
from pylint.checkers import BaseTokenChecker
from pylint.interfaces import IAstroidChecker, ITokenChecker, IRawChecker


def register(linter: pylint.lint.PyLinter) -> None:
    """Register the trailing commas checker."""
    linter.register_checker(TrailingCommaChecker(linter))


Message = Tuple[str, Sequence[str], int]


OPEN_LIST = ('[', '{', '(',)
CLOSE_LIST = (']', '}', ')',)
SEPARATOR_LIST = (',',)
IGNORABLE_TOKEN_LIST = (
    tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
    tokenize.DEDENT, tokenize.COMMENT, tokenize.ENCODING,
    tokenize.ENDMARKER,
)


class Token:
    """Wrapper for a single token structure."""
    def __init__(self, token_wrapper: 'TokenListWrapper', index: int) -> None:
        self.__token_wrapper = token_wrapper
        self.__index = index

    @property
    def index(self) -> int:
        """token number"""
        return self.__index

    @property
    def token_text(self) -> str:
        """text of this token"""
        return self.__token_wrapper.token_text(self.__index)

    @property
    def token_type(self) -> int:
        """token category"""
        return self.__token_wrapper.token_type(self.__index)

    @property
    def start_line_no(self) -> int:
        """line number for this token"""
        return self.__token_wrapper.start_line_no(self.__index)

    @property
    def start_col_no(self) -> int:
        """Starting column number for this token"""
        return self.__token_wrapper.start_col_no(self.__index)

    @property
    def end_line_no(self) -> int:
        """line number for this token"""
        return self.__token_wrapper.end_line_no(self.__index)

    @property
    def end_col_no(self) -> int:
        """Ending column number for this token"""
        return self.__token_wrapper.end_col_no(self.__index)

    @property
    def source_line(self) -> str:
        """Source code line for this token"""
        return self.__token_wrapper.source_line(self.__index)

    @property
    def next(self) -> Optional['Token']:
        """Next token in the list"""
        next_idx = self.__index + 1
        if next_idx >= self.__token_wrapper.count():
            return None
        return Token(self.__token_wrapper, next_idx)

    @property
    def prev(self) -> Optional['Token']:
        """Previous token in the list"""
        prev_idx = self.__index - 1
        if prev_idx < 0:
            return None
        return Token(self.__token_wrapper, prev_idx)

    def __repr__(self) -> str:
        return self.__token_wrapper.repr_item(self.__index)


class TokenListWrapper:
    """Wrapper around the whole list of tokens"""
    def __init__(self, token_list) -> None:
        self.__token_list = token_list

    def count(self) -> int:
        """number of tokens"""
        return len(self.__token_list)

    def token_text(self, idx: int) -> str:
        """token text"""
        return self.__token_list[idx][1]

    def token_type(self, idx: int) -> int:
        """tokenize type"""
        return self.__token_list[idx][0]

    def start_line_no(self, idx: int) -> int:
        """line number of the first line for the token"""
        return self.__token_list[idx][2][0]

    def start_col_no(self, idx: int) -> int:
        """column number for the start of the token"""
        return self.__token_list[idx][2][1]

    def end_line_no(self, idx: int) -> int:
        """line number of the last line for the token"""
        return self.__token_list[idx][3][0]

    def end_col_no(self, idx: int) -> int:
        """column number for the last of the token"""
        return self.__token_list[idx][3][1]

    def source_line(self, idx: int):
        """source text that contains the whole token"""
        return self.__token_list[idx][4]

    def get(self, idx: int) -> Token:
        """get a single wrapped token by index"""
        return self.__token_list[idx]

    def items(self) -> List[Token]:
        """all the items in the list (memory inefficient)"""
        ret: List[Token] = []
        for i in range(0, self.count()):
            ret.append(Token(self, i))
        return ret

    def repr_item(self, idx: int) -> str:
        """representation of a single index"""
        return repr(self.__token_list[idx])


class BracketContext:  # pylint: disable=too-many-instance-attributes
    """Context within a bracket"""
    def __init__(self, starting_token: Token, config) -> None:
        self._starting_token_line_no = starting_token.start_line_no
        self._current_line_no = starting_token.start_line_no
        self._previous_line_ended_with_string = False
        self._current_token: List[Token] = []
        self._current_line_items: List[Sequence[Token]] = []
        self._previous_was_comma = False
        self._item_count = 0
        self._is_empty = True
        self._config = config
        self._messages: List[Message] = []
        self._starting_token_text = None

        # figure out if this is a tuple, if, or a function call.
        self._expression_type = None
        self._starting_token_text = starting_token.token_text
        prev = starting_token.prev
        if (
                prev and
                prev.token_text in ('if', 'elif',) and
                starting_token.token_text == '('
        ):
            # if statements might begin with a tuple.  If it only contains a parenthetical
            # expression, then we can ignore it.
            self._expression_type = 'if'
        elif (
                prev and
                prev.token_type != tokenize.NAME and
                starting_token.token_text == '('
        ):
            self._expression_type = 'tuple'
        elif (
                prev and
                prev.token_type == tokenize.NAME and
                starting_token.token_text == '['
        ):
            # Only defining as list_access so it is not interpreted as a list
            self._expression_type = 'list_access'
        # else:
        #     print(f"Found list start, not if or elif or tuple, {prev} / {starting_token}")

    def started_sub_bracket(self, token: Token) -> List[Message]:
        """Start of a sub-bracket within this bracket."""
        # This should be treated like any other token, but it can spread across
        # multiple lines.  In this case, the start of the sub-bracket is just
        # the first part of a long token.
        self._is_empty = False
        self._current_token.append(token)
        return []

    def ended_sub_bracket(self, token: Token) -> List[Message]:
        """End of a sub-bracket within the this bracket."""
        # act like whatever was in the bracket is part of the same line.
        self._is_empty = False
        self._current_token.append(token)
        if self._starting_token_line_no == self._current_line_no:
            # the start of the bracket was on the starting line, so consider this the
            # new start of the expression
            self._starting_token_line_no = token.start_line_no
        self._current_line_no = token.start_line_no
        self._previous_was_comma = False
        return []

    def encountered_separator(self, token: Token) -> List[Message]:
        """a list separator in the bracket."""
        self._is_empty = False

        # if the separator is on a different line than the last token, then that's
        # a problem.
        if (
                token.start_line_no != self._current_line_no and
                self._is_expression_enabled()
        ):
            assert len(self._current_token) <= 0
            self._messages.append(("leading-comma", [], token.start_line_no,))

        if self._current_token:
            self._current_line_items.append(self._current_token)
            self._item_count += 1
        self._current_token = []

        self._previous_was_comma = True

        return []

    def encountered_token(self, token: Token) -> List[Message]:
        """An item token in the bracket"""
        self._is_empty = False

        if token.token_text == 'for' and self._expression_type is None:
            # this is most likely a [x for x in y] style list...
            self._expression_type = 'for'

        self._current_token.append(token)
        self._previous_was_comma = False

        return []

    def encountered_newline(self, token: Token) -> List[Message]:
        """Newline in the bracket"""

        # Don't look at the comma presence or adjust it.

        if self._current_token:
            self._current_line_items.append(self._current_token)
            # do not increment the number of discovered items until a separator
            # or end-of-bracket is found.

        if (
                self._config.one_item_per_line and
                len(self._current_line_items) > 1 and
                self._is_expression_enabled()
        ):
            # if we are on an if or for statement, then we shouldn't have more than 1
            # item in the bracket expression.  So we don't need to check for that
            # case here.
            self._messages.append(("multiple-items-per-line", [], token.start_line_no))
        elif (
                token.start_line_no == self._starting_token_line_no and
                len(self._current_line_items) >= 1 and
                self._is_expression_enabled()
        ):
            # items on the same line as the open bracket, but no closing bracket on
            # that line.
            # This is still valid for the "for" and "if" scenarios.
            self._messages.append(("multi-line-list-first-line-item", [], token.start_line_no))

        next_item = token.next
        if next_item:
            self._current_line_no = next_item.start_line_no
        self._current_token = []
        self._current_line_items = []

        return []

    def end(self, token: Token) -> List[Message]:
        """End of the bracket"""
        if self._expression_type == 'for':
            # For expressions don't need the comma check stuff.
            return []

        if self._current_token:
            self._current_line_items.append(self._current_token)
            self._item_count += 1

        if self._expression_type == 'if':
            # If the next token after the end is a ':', then this is a parenthetical
            # expression to wrap a multi-line if condition.  These can ignore the
            # trailing comma logic below.  There shouldn't be a newline after the ) before the :.
            next_token = token.next
            if next_token and next_token.token_text == ':':
                return self._messages

        if (
                self._expression_type == 'tuple' and
                self._config.comma_always_after_last_tuple and
                not self._previous_was_comma
        ):
            self._messages.append(("tuple-final-comma", [], token.start_line_no))

        # If the end token is on the same line number as the start brace, then
        # the syntax checking rules don't apply, except for the tuple stuff.
        # If the token is multi-line (like a concatenated string), then
        # it will be considered for this logic, too.
        if (
                token.end_line_no != self._starting_token_line_no and
                self._expression_type != 'list_access'
        ):
            if (
                    len(self._current_line_items) > 0 and
                    self._is_expression_enabled()
            ):
                self._messages.append(("multi-line-list-eol-close", [], token.start_line_no))
            prev = token.prev
            if not prev:
                prev = token
            if not self._previous_was_comma:
                # Exceptional situation check.
                # If the item count is 1, then this is a potential situation of
                # parenthesis to have a single line wrap.  For now, this does not
                # enforce the need for a closing comma.
                if self._item_count <= 1 and token.token_text == ')':
                    pass
                # Exception situation check.
                # If empty (whitespace only), then no commas expected
                elif self._is_empty:
                    pass
                elif self._is_expression_enabled():
                    self._messages.append(("closing-comma", [], prev.start_line_no))
                    # print(f"-- {self._item_count} items before ending {token}")

        return self._messages

    def _is_expression_enabled(self):
        """Checks whether the expression type is supported and enabled."""
        # if (
        #         self._expression_type == 'for' and
        #         self._config.ignore_multi_line_for
        # ):
        #     return False
        if (
                self._expression_type == 'if' and
                self._config.ignore_multi_line_if
        ):
            return False
        if (
                self._expression_type == 'tuple' and
                self._config.ignore_multi_line_tuple
        ):
            return False
        if (
                self._starting_token_text == '(' and
                self._expression_type is None and
                self._config.ignore_function_def
        ):
            return False
        return True


class TrailingCommaChecker(BaseTokenChecker):
    """
    Trailing commas looks at the raw data and syntax tree.

    This will enforce the multi-line brace / parenthesis format of:
        (
            this,
            is,
            correctly,
            formatted,
        )

    As opposed to this:
        (this,
            is,
            not,
            right)

    Scenarios that require commas:
        _ after last item on a line in a list, tuple, or dictionary (includes argument list)

    Scenarios that don't require commas:
        _ list on the same line:
            (x, y, z)
        _ wrapper around a string concatenation:
            (
                "a "
                "b "
                "c d e"
            )

    The one weird situation that is incorrectly trapped is the parenthesis for
    wrapping multi-lines:
        (
            A +
            B -
            C *
            (x + y)
        )
    But here, those parenthesis aren't needed.
    """

    __implements__ = (ITokenChecker, IAstroidChecker, IRawChecker)

    name = 'trailing-comma'
    priority = -1

    msgs = {
        'C9201': (
            "No trailing comma",
            "trailing-comma",
            "Used when a list, tuple, or dict does not have a trailing comma at the end of a line.",
        ),
        'C9202': (
            "Leading comma",
            "leading-comma",
            "A line started with a comma.",
        ),
        'C9203': (
            "No closing comma",
            "closing-comma",
            "A list, tuple, or dict did not have a comma before the closing bracket.",
        ),
        'C9204': (
            "More than 1 item per line for multi-line list",
            "multiple-items-per-line",
            "A list, tuple, or dict had more than 1 item on a line, for lists spread across lines.",
        ),
        'C9205': (
            "No final tuple comma",
            "tuple-final-comma",
            "Tuples must have a comma after hte last item.",
        ),
        'C9206': (
            "Multi-line list but items on first line",
            "multi-line-list-first-line-item",
            "A list, tuple, or dict that spread across multiple lines had an item on the "
            "first line.",
        ),
        'C9207': (
            "Multi-line list does not close on its own line",
            "multi-line-list-eol-close",
            "A multi-line list, tuple, or dict must not have an item on the same line as "
            "the closing bracket.",
        ),
    }

    options = (
        (
            'comma-always-after-last-tuple',
            {
                'default': False,
                "type": "yn",
                "metavar": "<y_or_n>",
                'help':
                    "Require a comma after the last item in a tuple, "
                    "regardless of the location of the closing token",
            },
        ),
        (
            'one-item-per-line',
            {
                'default': False,
                "type": "yn",
                "metavar": "<y_or_n>",
                'help':
                    "Require that at most 1 item in the list can be on each line.",
            },
        ),
        # (
        #     'ignore-multi-line-for',
        #     {
        #         'default': False,
        #         "type": "yn",
        #         "metavar": "<y_or_n>",
        #         'help':
        #             "Whether multi-line `for` statements should enforce"
        #             "trailing comma and start/end line requirements.",
        #     },
        # ),
        (
            'ignore-multi-line-if',
            {
                'default': False,
                "type": "yn",
                "metavar": "<y_or_n>",
                'help':
                    "Whether multi-line `if` statements should enforce"
                    "trailing comma and start/end line requirements.",
            },
        ),
        (
            'ignore-multi-line-tuple',
            {
                'default': False,
                "type": "yn",
                "metavar": "<y_or_n>",
                'help':
                    "Whether multi-line tuple statements should enforce"
                    "trailing comma and start/end line requirements.",
            },
        ),
        (
            'ignore-function-def',
            {
                'default': False,
                "type": "yn",
                "metavar": "<y_or_n>",
                'help':
                    "Whether to the definition of a function and its "
                    "parameters should enforce trailing comma and start/end "
                    "line requirements.",
            },
        ),
    )

    def __init__(self, linter: pylint.lint.PyLinter):
        super().__init__(linter)
        self._open_brace_lines: List[BracketContext] = []

    def process_module(self, module):
        """The start of a new module file's processing."""
        # Do nothing.

    def process_tokens(self, tokens):
        """process tokens and search for:

         _ a line in a list, that isn't on the same line as the open character,
           or end with the closing character, that doesn't end with a comma.
           The exception is a list generator.
        """
        # print("TRAILING_COMMAS - PROCESSING TOKENS")
        # print(repr(tokens))
        line_num = 0
        self._open_brace_lines = []

        token_list = TokenListWrapper(tokens)
        for token in token_list.items():
            if token.start_line_no != line_num:
                # Moved to another line of tokens.
                line_num = token.start_line_no
            # tokenize.NEWLINE == moved to the next logical line
            if token.token_type == tokenize.NL:
                # A physical newline...
                self._ended_line(token)
            elif token.token_text in OPEN_LIST:
                self._enter_bracket(token)
            elif token.token_text in CLOSE_LIST:
                self._exit_bracket(token)
            elif token.token_text in SEPARATOR_LIST:
                self._separator(token)
            elif token.token_type not in IGNORABLE_TOKEN_LIST:
                # This is a real program token.
                self._found_token(token)

    def _enter_bracket(self, token: Token) -> None:
        # print(f" - entered bracket on {token}")
        if self._open_brace_lines:
            self._add_messages(self._open_brace_lines[-1].started_sub_bracket(token))
        self._open_brace_lines.append(BracketContext(token, self.config))

    def _exit_bracket(self, token: Token) -> None:
        # print(f" - exited bracket on {token}")
        if self._open_brace_lines:
            prev = self._open_brace_lines.pop()
            self._add_messages(prev.end(token))
            if self._open_brace_lines:
                self._add_messages(self._open_brace_lines[-1].ended_sub_bracket(token))

    def _separator(self, token: Token) -> None:
        # print(f" - encountered separator on {token}")
        if self._open_brace_lines:
            self._add_messages(self._open_brace_lines[-1].encountered_separator(token))

    def _found_token(self, token: Token) -> None:
        # print(f" - found other token {token}")
        if self._open_brace_lines:
            self._add_messages(self._open_brace_lines[-1].encountered_token(token))

    def _ended_line(self, token: Token) -> None:
        # print(f" - found EOF {token}")
        if self._open_brace_lines:
            self._add_messages(self._open_brace_lines[-1].encountered_newline(token))

    def _add_messages(self, messages: List[Message]) -> None:
        for msg_id, args, line in messages:
            self.add_message(
                msgid=msg_id,
                args=args,
                line=line,
            )
