#!/usr/bin/env python3
"""Adversarial checks for false passes in compact ranking validation."""
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('ranking', Path(__file__).with_name('verify-bar-ranking.py'))
ranking = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ranking)


class RankingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = ranking.VARIANTS[0].read_text(encoding='utf-8')

    def test_shipped_variants(self):
        sources = [path.read_text(encoding='utf-8') for path in ranking.VARIANTS]
        for source in sources:
            self.assertEqual(ranking.verify(source), [])
        self.assertEqual(len({ranking.signature(source) for source in sources}), 1)

    def reject(self, old, new, finding):
        self.assertIn(old, self.source)
        errors = ranking.verify(self.source.replace(old, new, 1))
        self.assertTrue(any(finding in error for error in errors), errors)

    def test_geometry_and_labels(self):
        for old, new, finding in [
            ('width="524.000"', 'width="520.000"', 'bar length'),
            ('class="bar" x="148"', 'class="bar" x="152"', 'baseline'),
            ('data-axis-min="0"', 'data-axis-min="10"', 'zero'),
            ('data-axis-max="70"', 'data-axis-max="0"', 'positive'),
            ('data-value="65.5"', 'data-value="NaN"', 'non-finite'),
            ('data-value="48.5"', 'data-value="66.0"', 'sorted'),
            ('data-row-count="27"', 'data-row-count="26"', 'row count'),
            ('data-label="Danmark" font-weight="600">65,5 %', 'data-label="Danmark" font-weight="600">66,5 %', 'printed value'),
            ('data-focal="false"', 'data-focal="true"', 'focal country'),
        ]:
            with self.subTest(finding=finding):
                self.reject(old, new, finding)

    def test_missing_chart_fails_closed(self):
        self.assertTrue(ranking.verify('<html>No chart</html>'))
        self.assertTrue(ranking.verify('<svg xmlns="http://www.w3.org/2000/svg"></svg>'))

    def test_optional_benchmarks(self):
        source = self.source.replace('</svg>', '''<line data-benchmark="eu-weighted" data-value="37.9" x1="451.200" x2="451.200"/>
<line data-benchmark="median" data-value="35.7" x1="433.600" x2="433.600"/>
</svg>''')
        self.assertEqual(ranking.verify(source), [])
        shifted = source.replace('x1="451.200"', 'x1="455.200"')
        self.assertTrue(any('shifted benchmark' in error for error in ranking.verify(shifted)))
        wrong_median = source.replace('data-benchmark="median" data-value="35.7"', 'data-benchmark="median" data-value="36.0"')
        self.assertTrue(any('median does not match' in error for error in ranking.verify(wrong_median)))

    def test_tied_country_values_are_valid(self):
        self.assertIn('data-country="Cypern" data-value="40.7"', self.source)
        self.assertIn('data-country="Spanien" data-value="40.7"', self.source)
        self.assertEqual(ranking.verify(self.source), [])


if __name__ == '__main__':
    unittest.main()
