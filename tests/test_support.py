#
# Copyright (C) 2007-2011 Edgewall Software, 2013-2023 the Babel team
# All rights reserved.
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

import datetime
import inspect
import os
import shutil
import sys
import tempfile
import unittest
from decimal import Decimal
from io import BytesIO

import pytest

from babel import support
from babel.messages import Catalog
from babel.messages.mofile import write_mo

SKIP_LGETTEXT = sys.version_info >= (3, 8)


@pytest.mark.usefixtures("os_environ")
class TranslationsTestCase(unittest.TestCase):

    def setUp(self):
        # Use a locale which won't fail to run the tests
        os.environ['LANG'] = 'en_US.UTF-8'
        messages1 = [
            ('foo', {'string': 'Voh'}),
            ('foo', {'string': 'VohCTX', 'context': 'foo'}),
            (('foo1', 'foos1'), {'string': ('Voh1', 'Vohs1')}),
            (('foo1', 'foos1'), {'string': ('VohCTX1', 'VohsCTX1'), 'context': 'foo'}),
        ]
        messages2 = [
            ('foo', {'string': 'VohD'}),
            ('foo', {'string': 'VohCTXD', 'context': 'foo'}),
            (('foo1', 'foos1'), {'string': ('VohD1', 'VohsD1')}),
            (('foo1', 'foos1'), {'string': ('VohCTXD1', 'VohsCTXD1'), 'context': 'foo'}),
        ]
        catalog1 = Catalog(locale='en_GB', domain='messages')
        catalog2 = Catalog(locale='en_GB', domain='messages1')
        for ids, kwargs in messages1:
            catalog1.add(ids, **kwargs)
        for ids, kwargs in messages2:
            catalog2.add(ids, **kwargs)
        catalog1_fp = BytesIO()
        catalog2_fp = BytesIO()
        write_mo(catalog1_fp, catalog1)
        catalog1_fp.seek(0)
        write_mo(catalog2_fp, catalog2)
        catalog2_fp.seek(0)
        translations1 = support.Translations(catalog1_fp)
        translations2 = support.Translations(catalog2_fp, domain='messages1')
        self.translations = translations1.add(translations2, merge=False)

    def assertEqualTypeToo(self, expected, result):
        assert expected == result
        assert type(expected) == type(result), f"instance types do not match: {type(expected)!r}!={type(result)!r}"

    def test_pgettext(self):
        self.assertEqualTypeToo('Voh', self.translations.gettext('foo'))
        self.assertEqualTypeToo('VohCTX', self.translations.pgettext('foo',
                                                                     'foo'))

    def test_upgettext(self):
        self.assertEqualTypeToo('Voh', self.translations.ugettext('foo'))
        self.assertEqualTypeToo('VohCTX', self.translations.upgettext('foo',
                                                                      'foo'))

    @pytest.mark.skipif(SKIP_LGETTEXT, reason="lgettext is deprecated")
    def test_lpgettext(self):
        self.assertEqualTypeToo(b'Voh', self.translations.lgettext('foo'))
        self.assertEqualTypeToo(b'VohCTX', self.translations.lpgettext('foo',
                                                                       'foo'))

    def test_npgettext(self):
        self.assertEqualTypeToo('Voh1',
                                self.translations.ngettext('foo1', 'foos1', 1))
        self.assertEqualTypeToo('Vohs1',
                                self.translations.ngettext('foo1', 'foos1', 2))
        self.assertEqualTypeToo('VohCTX1',
                                self.translations.npgettext('foo', 'foo1',
                                                            'foos1', 1))
        self.assertEqualTypeToo('VohsCTX1',
                                self.translations.npgettext('foo', 'foo1',
                                                            'foos1', 2))

    def test_unpgettext(self):
        self.assertEqualTypeToo('Voh1',
                                self.translations.ungettext('foo1', 'foos1', 1))
        self.assertEqualTypeToo('Vohs1',
                                self.translations.ungettext('foo1', 'foos1', 2))
        self.assertEqualTypeToo('VohCTX1',
                                self.translations.unpgettext('foo', 'foo1',
                                                             'foos1', 1))
        self.assertEqualTypeToo('VohsCTX1',
                                self.translations.unpgettext('foo', 'foo1',
                                                             'foos1', 2))

    @pytest.mark.skipif(SKIP_LGETTEXT, reason="lgettext is deprecated")
    def test_lnpgettext(self):
        self.assertEqualTypeToo(b'Voh1',
                                self.translations.lngettext('foo1', 'foos1', 1))
        self.assertEqualTypeToo(b'Vohs1',
                                self.translations.lngettext('foo1', 'foos1', 2))
        self.assertEqualTypeToo(b'VohCTX1',
                                self.translations.lnpgettext('foo', 'foo1',
                                                             'foos1', 1))
        self.assertEqualTypeToo(b'VohsCTX1',
                                self.translations.lnpgettext('foo', 'foo1',
                                                             'foos1', 2))

    def test_dpgettext(self):
        self.assertEqualTypeToo(
            'VohD', self.translations.dgettext('messages1', 'foo'))
        self.assertEqualTypeToo(
            'VohCTXD', self.translations.dpgettext('messages1', 'foo', 'foo'))

    def test_dupgettext(self):
        self.assertEqualTypeToo(
            'VohD', self.translations.dugettext('messages1', 'foo'))
        self.assertEqualTypeToo(
            'VohCTXD', self.translations.dupgettext('messages1', 'foo', 'foo'))

    @pytest.mark.skipif(SKIP_LGETTEXT, reason="lgettext is deprecated")
    def test_ldpgettext(self):
        self.assertEqualTypeToo(
            b'VohD', self.translations.ldgettext('messages1', 'foo'))
        self.assertEqualTypeToo(
            b'VohCTXD', self.translations.ldpgettext('messages1', 'foo', 'foo'))

    def test_dnpgettext(self):
        self.assertEqualTypeToo(
            'VohD1', self.translations.dngettext('messages1', 'foo1', 'foos1', 1))
        self.assertEqualTypeToo(
            'VohsD1', self.translations.dngettext('messages1', 'foo1', 'foos1', 2))
        self.assertEqualTypeToo(
            'VohCTXD1', self.translations.dnpgettext('messages1', 'foo', 'foo1',
                                                     'foos1', 1))
        self.assertEqualTypeToo(
            'VohsCTXD1', self.translations.dnpgettext('messages1', 'foo', 'foo1',
                                                      'foos1', 2))

    def test_dunpgettext(self):
        self.assertEqualTypeToo(
            'VohD1', self.translations.dungettext('messages1', 'foo1', 'foos1', 1))
        self.assertEqualTypeToo(
            'VohsD1', self.translations.dungettext('messages1', 'foo1', 'foos1', 2))
        self.assertEqualTypeToo(
            'VohCTXD1', self.translations.dunpgettext('messages1', 'foo', 'foo1',
                                                      'foos1', 1))
        self.assertEqualTypeToo(
            'VohsCTXD1', self.translations.dunpgettext('messages1', 'foo', 'foo1',
                                                       'foos1', 2))

    @pytest.mark.skipif(SKIP_LGETTEXT, reason="lgettext is deprecated")
    def test_ldnpgettext(self):
        self.assertEqualTypeToo(
            b'VohD1', self.translations.ldngettext('messages1', 'foo1', 'foos1', 1))
        self.assertEqualTypeToo(
            b'VohsD1', self.translations.ldngettext('messages1', 'foo1', 'foos1', 2))
        self.assertEqualTypeToo(
            b'VohCTXD1', self.translations.ldnpgettext('messages1', 'foo', 'foo1',
                                                       'foos1', 1))
        self.assertEqualTypeToo(
            b'VohsCTXD1', self.translations.ldnpgettext('messages1', 'foo', 'foo1',
                                                        'foos1', 2))

    def test_load(self):
        tempdir = tempfile.mkdtemp()
        try:
            messages_dir = os.path.join(tempdir, 'fr', 'LC_MESSAGES')
            os.makedirs(messages_dir)
            catalog = Catalog(locale='fr', domain='messages')
            catalog.add('foo', 'bar')
            with open(os.path.join(messages_dir, 'messages.mo'), 'wb') as f:
                write_mo(f, catalog)

            translations = support.Translations.load(tempdir, locales=('fr',), domain='messages')
            assert translations.gettext('foo') == 'bar'
        finally:
            shutil.rmtree(tempdir)


class NullTranslationsTestCase(unittest.TestCase):

    def setUp(self):
        fp = BytesIO()
        write_mo(fp, Catalog(locale='de'))
        fp.seek(0)
        self.translations = support.Translations(fp=fp)
        self.null_translations = support.NullTranslations(fp=fp)

    def method_names(self):
        names = [name for name in dir(self.translations) if 'gettext' in name]
        if SKIP_LGETTEXT:
            # Remove deprecated l*gettext functions
            names = [name for name in names if not name.startswith('l')]
        return names

    def test_same_methods(self):
        for name in self.method_names():
            if not hasattr(self.null_translations, name):
                self.fail(f"NullTranslations does not provide method {name!r}")

    def test_method_signature_compatibility(self):
        for name in self.method_names():
            translations_method = getattr(self.translations, name)
            null_method = getattr(self.null_translations, name)
            assert inspect.getfullargspec(translations_method) == inspect.getfullargspec(null_method)

    def test_same_return_values(self):
        data = {
            'message': 'foo', 'domain': 'domain', 'context': 'tests',
            'singular': 'bar', 'plural': 'baz', 'num': 1,
            'msgid1': 'bar', 'msgid2': 'baz', 'n': 1,
        }
        for name in self.method_names():
            method = getattr(self.translations, name)
            null_method = getattr(self.null_translations, name)
            signature = inspect.getfullargspec(method)
            parameter_names = [name for name in signature.args if name != 'self']
            values = [data[name] for name in parameter_names]
            assert method(*values) == null_method(*values)


class LazyProxyTestCase(unittest.TestCase):

    def test_proxy_caches_result_of_function_call(self):
        self.counter = 0

        def add_one():
            self.counter += 1
            return self.counter
        proxy = support.LazyProxy(add_one)
        assert proxy.value == 1
        assert proxy.value == 1

    def test_can_disable_proxy_cache(self):
        self.counter = 0

        def add_one():
            self.counter += 1
            return self.counter
        proxy = support.LazyProxy(add_one, enable_cache=False)
        assert proxy.value == 1
        assert proxy.value == 2

    def test_can_copy_proxy(self):
        from copy import copy

        numbers = [1, 2]

        def first(xs):
            return xs[0]

        proxy = support.LazyProxy(first, numbers)
        proxy_copy = copy(proxy)

        numbers.pop(0)
        assert proxy.value == 2
        assert proxy_copy.value == 2

    def test_can_deepcopy_proxy(self):
        from copy import deepcopy
        numbers = [1, 2]

        def first(xs):
            return xs[0]

        proxy = support.LazyProxy(first, numbers)
        proxy_deepcopy = deepcopy(proxy)

        numbers.pop(0)
        assert proxy.value == 2
        assert proxy_deepcopy.value == 1

    def test_handle_attribute_error(self):

        def raise_attribute_error():
            raise AttributeError('message')

        proxy = support.LazyProxy(raise_attribute_error)
        with pytest.raises(AttributeError) as exception:
            _ = proxy.value

        assert str(exception.value) == 'message'


class TestFormat:
    def test_format_datetime(self, timezone_getter):
        when = datetime.datetime(2007, 4, 1, 15, 30)
        fmt = support.Format('en_US', tzinfo=timezone_getter('US/Eastern'))
        assert fmt.datetime(when) == 'Apr 1, 2007, 11:30:00\u202fAM'

    def test_format_time(self, timezone_getter):
        when = datetime.datetime(2007, 4, 1, 15, 30)
        fmt = support.Format('en_US', tzinfo=timezone_getter('US/Eastern'))
        assert fmt.time(when) == '11:30:00\u202fAM'

    def test_format_number(self):
        assert support.Format('en_US').number(1234) == '1,234'
        assert support.Format('ar_EG', numbering_system="default").number(1234) == '1٬234'

    def test_format_decimal(self):
        assert support.Format('en_US').decimal(1234.5) == '1,234.5'
        assert support.Format('en_US').decimal(Decimal("1234.5")) == '1,234.5'
        assert support.Format('ar_EG', numbering_system="default").decimal(1234.5) == '1٬234٫5'
        assert support.Format('ar_EG', numbering_system="default").decimal(Decimal("1234.5")) == '1٬234٫5'

    def test_format_compact_decimal(self):
        assert support.Format('en_US').compact_decimal(1234) == '1K'
        assert support.Format('ar_EG', numbering_system="default").compact_decimal(
            1234, fraction_digits=1) == '1٫2\xa0ألف'
        assert support.Format('ar_EG', numbering_system="default").compact_decimal(
            Decimal("1234"), fraction_digits=1) == '1٫2\xa0ألف'

    def test_format_currency(self):
        assert support.Format('en_US').currency(1099.98, 'USD') == '$1,099.98'
        assert support.Format('en_US').currency(Decimal("1099.98"), 'USD') == '$1,099.98'
        assert support.Format('ar_EG', numbering_system="default").currency(
            1099.98, 'EGP') == '\u200f1٬099٫98\xa0ج.م.\u200f'

    def test_format_compact_currency(self):
        assert support.Format('en_US').compact_currency(1099.98, 'USD') == '$1K'
        assert support.Format('en_US').compact_currency(Decimal("1099.98"), 'USD') == '$1K'
        assert support.Format('ar_EG', numbering_system="default").compact_currency(
            1099.98, 'EGP') == '1\xa0ألف\xa0ج.م.\u200f'

    def test_format_percent(self):
        assert support.Format('en_US').percent(0.34) == '34%'
        assert support.Format('en_US').percent(Decimal("0.34")) == '34%'
        assert support.Format('ar_EG', numbering_system="default").percent(134.5) == '13٬450%'

    def test_format_scientific(self):
        assert support.Format('en_US').scientific(10000) == '1E4'
        assert support.Format('en_US').scientific(Decimal("10000")) == '1E4'
        assert support.Format('ar_EG', numbering_system="default").scientific(10000) == '1أس4'


def test_lazy_proxy():
    def greeting(name='world'):
        return f"Hello, {name}!"

    lazy_greeting = support.LazyProxy(greeting, name='Joe')
    assert str(lazy_greeting) == "Hello, Joe!"
    assert '  ' + lazy_greeting == '  Hello, Joe!'
    assert '(%s)' % lazy_greeting == '(Hello, Joe!)'
    assert f"[{lazy_greeting}]" == "[Hello, Joe!]"

    greetings = sorted([
        support.LazyProxy(greeting, 'world'),
        support.LazyProxy(greeting, 'Joe'),
        support.LazyProxy(greeting, 'universe'),
    ])
    assert [str(g) for g in greetings] == [
        "Hello, Joe!",
        "Hello, universe!",
        "Hello, world!",
    ]


def test_catalog_merge_files():
    # Refs issues #92, #162
    t1 = support.Translations()
    assert t1.files == []
    t1._catalog["foo"] = "bar"
    fp = BytesIO()
    write_mo(fp, Catalog())
    fp.seek(0)
    fp.name = "pro.mo"
    t2 = support.Translations(fp)
    assert t2.files == ["pro.mo"]
    t2._catalog["bar"] = "quux"
    t1.merge(t2)
    assert t1.files == ["pro.mo"]
    assert set(t1._catalog.keys()) == {'', 'foo', 'bar'}
