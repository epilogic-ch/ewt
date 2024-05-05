"""
    pygments.lexers.javascript
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Lexers for JavaScript and related languages.

    :copyright: Copyright 2006-2023 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re

from pygments.lexer import bygroups, combined, default, do_insertions, include, \
    inherit, Lexer, RegexLexer, this, using, words, line_re
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Punctuation, Other, Generic, Whitespace
from pygments.util import get_bool_opt
import pygments.unistring as uni

__all__ = ['EwtsLexer']

JS_IDENT_START = ('(?:[$_' + uni.combine('Lu', 'Ll', 'Lt', 'Lm', 'Lo', 'Nl') +
                  ']|\\\\u[a-fA-F0-9]{4})')
JS_IDENT_PART = ('(?:[$' + uni.combine('Lu', 'Ll', 'Lt', 'Lm', 'Lo', 'Nl',
                                       'Mn', 'Mc', 'Nd', 'Pc') +
                 '\u200c\u200d]|\\\\u[a-fA-F0-9]{4})')
JS_IDENT = JS_IDENT_START + '(?:' + JS_IDENT_PART + ')*'


class EwtsLexer(RegexLexer):
    """
    For JavaScript source code.
    """

    name = 'Ewts'
    aliases = ['ewts']
    filenames = ['*.ewts', '*.script', '*.ewtsub', '*.subscript']

    flags = re.DOTALL | re.MULTILINE

    tokens = {
        'commentsandwhitespace': [
            (r'\s+', Whitespace),
            (r'<!--', Comment),
            (r'//.*?$', Comment.Single),
            (r'/\*.*?\*/', Comment.Multiline)
        ],
        'slashstartsregex': [
            include('commentsandwhitespace'),
            (r'/(\\.|[^[/\\\n]|\[(\\.|[^\]\\\n])*])+/'
             r'([gimuysd]+\b|\B)', String.Regex, '#pop'),
            (r'(?=/)', Text, ('#pop', 'badregex')),
            default('#pop')
        ],
        'badregex': [
            (r'\n', Whitespace, '#pop')
        ],
        'root': [
            (r'\A#! ?/.*?$', Comment.Hashbang),  # recognized by node.js
            (r'^(?=\s|/|<!--)', Text, 'slashstartsregex'),
            include('commentsandwhitespace'),

            # Numeric literals
            (r'0[bB][01]+n?', Number.Bin),
            (r'0[oO]?[0-7]+n?', Number.Oct),  # Browsers support "0o7" and "07" (< ES5) notations
            (r'0[xX][0-9a-fA-F]+n?', Number.Hex),
            (r'[0-9]+n', Number.Integer),  # Javascript BigInt requires an "n" postfix
            # Javascript doesn't have actual integer literals, so every other
            # numeric literal is handled by the regex below (including "normal")
            # integers
            (r'(\.[0-9]+|[0-9]+\.[0-9]*|[0-9]+)([eE][-+]?[0-9]+)?', Number.Float),

            (r'\.\.\.|=>', Punctuation),
            (r'\+\+|--|~|\?\?=?|\?|:|\\(?=\n)|'
             r'(<<|>>>?|==?|!=?|(?:\*\*|\|\||&&|[-<>+*%&|^/]))=?', Operator, 'slashstartsregex'),
            (r'[{(\[;,]', Punctuation, 'slashstartsregex'),
            (r'[})\].]', Punctuation),

            (r'(typeof|instanceof|in|void|delete|new)\b', Operator.Word, 'slashstartsregex'),

            # Match stuff like: constructor
            (r'\b(constructor|from|as)\b', Keyword.Reserved),

            (r'(for|in|while|do|break|return|continue|switch|case|default|if|else|'
             r'throw|try|catch|finally|yield|await|async|this|of|static|export|'
             r'import|debugger|extends|super)\b', Keyword, 'slashstartsregex'),
            (r'(var|let|const|with|function|class)\b', Keyword.Declaration, 'slashstartsregex'),

            (r'(abstract|boolean|byte|char|double|enum|final|float|goto|'
             r'implements|int|interface|long|native|package|private|protected|'
             r'public|short|synchronized|throws|transient|volatile)\b', Keyword.Reserved),
            (r'(true|false|null|NaN|Infinity|undefined)\b', Keyword.Constant),

            (r'(Array|Boolean|Date|BigInt|Function|Math|ArrayBuffer|'
             r'Number|Object|RegExp|String|Promise|Proxy|decodeURI|'
             r'decodeURIComponent|encodeURI|encodeURIComponent|'
             r'eval|isFinite|isNaN|parseFloat|parseInt|DataView|'
             r'document|window|globalThis|global|Symbol|Intl|'
             r'WeakSet|WeakMap|Set|Map|Reflect|JSON|Atomics|'
             r'Int(?:8|16|32)Array|BigInt64Array|Float32Array|Float64Array|'
             r'Uint8ClampedArray|Uint(?:8|16|32)Array|BigUint64Array)\b', Name.Builtin),

            (r'((?:Eval|Internal|Range|Reference|Syntax|Type|URI)?Error)\b', Name.Exception),

            # Match stuff like: super(argument, list)
            (r'(super)(\s*)(\([\w,?.$\s]+\s*\))',
             bygroups(Keyword, Whitespace), 'slashstartsregex'),
            # Match stuff like: function() {...}
            (r'([a-zA-Z_?.$][\w?.$]*)(?=\(\) \{)', Name.Other, 'slashstartsregex'),

            (JS_IDENT, Name.Other),
            (r'"(\\\\|\\[^\\]|[^"\\])*"', String.Double),
            (r"'(\\\\|\\[^\\]|[^'\\])*'", String.Single),
            (r'`', String.Backtick, 'interp'),
        ],
        'interp': [
            (r'`', String.Backtick, '#pop'),
            (r'\\.', String.Backtick),
            (r'\$\{', String.Interpol, 'interp-inside'),
            (r'\$', String.Backtick),
            (r'[^`\\$]+', String.Backtick),
        ],
        'interp-inside': [
            # TODO: should this include single-line comments and allow nesting strings?
            (r'\}', String.Interpol, '#pop'),
            include('root'),
        ],
    }

