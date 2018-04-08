# -*- coding: utf-8 -*-
import re
import datetime


class TokenBase:

    def __init__(self, string: str):
        self.string = string

    def __len__(self):
        return len(self.string)

    def __str__(self):
        return self.string

    def as_args(self):
        return [self.string]

    def as_kwargs(self):
        return {}


class RawToken(TokenBase):
    pass


class RegexToken(RawToken):

    def __init__(self, match):
        start, end = match.span()
        super().__init__(match.string[start:end])
        self.match = match

    def as_args(self):
        if self.match.groupdict():
            return []
        return self.match.groups()

    def as_kwargs(self):
        return self.match.groupdict()


class ProperNounToken(RawToken):

    def __init__(self, string: str, normalize: str):
        super().__init__(string)
        self.normalize = normalize

    def __str__(self):
        return self.normalize

    def as_args(self):
        return []

    def as_kwargs(self):
        return {self.normalize: self.string}


class DateToken(TokenBase):

    def __init__(self, date: datetime.date, string: str):
        super().__init__(string)
        self.date = date

    def as_args(self):
        return [self.date]


class TokenizerBase:

    def match(self, string: str):
        raise NotImplemented


class RegexTokenizer(TokenizerBase):

    def __init__(self, pattern, flag=0, **kwargs):
        super().__init__(**kwargs)
        self.re = re.compile(pattern, flag)

    def match(self, string: str):
        m = self.re.search(string)
        if m is not None:
            return RegexToken(m), m.start()


class DateTokenizer(TokenizerBase):

    @classmethod
    def _from_re(cls, date, m):
        start, end = m.span()
        return DateToken(date, m.string[start:end])

    @classmethod
    def _m_01(cls, string):
        if not hasattr(cls, '_re_01'):
            cls._re_01 = re.compile(r'(\d+)[/年-](\d+)[/月-](\d+)日?')
        m = cls._re_01.search(string)
        if m is None:
            return
        year, month, day = map(int, m.groups())
        if 0 <= year <= 51:
            year += 2000
        elif year < 100:
            year += 1900
        try:
            return cls._from_re(datetime.date(year, month, day), m)
        except ValueError:
            return

    @classmethod
    def _m_02(cls, string):
        if not hasattr(cls, '_re_02'):
            cls._re_02 = re.compile(f'(\d+)[/月-](\d+)日?(?:\s?[(（][月火水木金土日][)）])?')
        m = cls._re_02.search(string)
        if m is None:
            return
        month, day = map(int, m.groups())
        today = datetime.date.today()
        date_candidates = []
        for dy in [-1, 0, 1]:
            try:
                date = datetime.date(today.year + dy, month, day)
            except ValueError:
                continue
            date_candidates.append(date)
        if date_candidates:
            date = min(date_candidates, key=lambda d: abs((d - today).days))
            return cls._from_re(date, m)

    @classmethod
    def _m_03(cls, string):
        if not hasattr(cls, '_re_03'):
            cls._re_03 = re.compile(r'(今週|来週|先週|再来週|先々週|)([月火水木金土日])曜')
        m = cls._re_03.search(string)
        if m is None:
            return
        weeks, weekday = m.groups()
        if not weeks:
            weeks = '今週'
        weeks = {'今週': 0, '来週': 1, '先週': -1, '再来週': 2, '先々週': -2}[weeks]
        weekday = '月火水木金土日'.index(weekday)
        today = datetime.date.today()
        date = today + datetime.timedelta(weeks=weeks, days=weekday - today.weekday())
        return cls._from_re(date, m)

    @classmethod
    def _m_04(cls, string):
        if not hasattr(cls, '_re_04'):
            cls._re_04 = re.compile(r'(\d+)日')
        m = cls._re_04.search(string)
        if m is None:
            return
        day = int(m.group(1))
        today = datetime.date.today()
        try:
            date = datetime.date(today.year, today.month, day)
        except ValueError:
            return
        return cls._from_re(date, m)

    @classmethod
    def _m_05(cls, string):
        proper_days = {
            'today': 0,
            '今日': 0,
            '本日': 0,
            'tomorrow': 1,
            '明日': 1,
            'yesterday': -1,
            '昨日': -1,
            '明後日': 2,
            '一昨日': -2,
        }
        if not hasattr(cls, '_re_05'):
            cls._re_05 = re.compile(r'(%s)' % '|'.join(proper_days), re.IGNORECASE)
        m = cls._re_05.search(string)
        if m is None:
            return
        days = m.group(1).lower()
        date = datetime.date.today() + datetime.timedelta(days=proper_days[days])
        return cls._from_re(date, m)

    def match(self, string: str):
        tokens = []
        for i in range(1, 6):
            method = getattr(self, '_m_%2.2i' % i)
            res = method(string)
            if res is not None:
                tokens.append(res)
        if tokens:
            return max(tokens, key=lambda x: len(x[0]))


class Matcher:

    def __init__(self, tokenizer_list):
        self.tokenizer_list = tokenizer_list

    def match(self, string: str):
        origin = string
        args = []
        kwargs = {}
        for tokenizer in self.tokenizer_list:
            res = tokenizer.match(string)
            if res is None:
                return
            t, start = res
            if string[:start].strip():
                return
            string = string[start + len(t):]
            args.extend(t.as_args())
            kwargs.update(t.as_kwargs())
        return MatchResult(origin, args, kwargs)


class MatchResult:

    def __init__(self, origin: str, args, kwargs):
        self.origin = origin
        self.args = args
        self.kwargs = kwargs
