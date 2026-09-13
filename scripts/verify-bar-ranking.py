#!/usr/bin/env python3
"""Check compact ranking geometry and the shipped variants; standard library only.

This verifies internal consistency of the declared values, not source accuracy.
Usage: python scripts/verify-bar-ranking.py [example.html ...]
"""
from __future__ import annotations

import math
import re
import statistics
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'skills/diagram-design/assets'
VARIANTS = tuple(ASSETS / f'example-bar-ranking{v}.html' for v in ('', '-dark', '-full'))
NS = {'s': 'http://www.w3.org/2000/svg'}


def number(value: str) -> float:
    result = float(value.replace('%', '').replace(' ', '').replace(',', '.'))
    if not math.isfinite(result):
        raise ValueError('non-finite value')
    return result


def svg_root(source: str) -> ET.Element:
    match = re.search(r'<svg\b.*?</svg>', source, re.S)
    if not match:
        raise ValueError('missing SVG')
    return ET.fromstring(match.group())


def verify(source: str) -> list[str]:
    errors = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    def close(actual: float, expected: float, message: str) -> None:
        require(math.isclose(actual, expected, abs_tol=0.01), message)

    try:
        svg = svg_root(source)
        require(svg.get('data-chart') == 'bar-ranking', 'missing ranking contract')
        minimum = number(svg.attrib['data-axis-min'])
        maximum = number(svg.attrib['data-axis-max'])
        left = number(svg.attrib['data-plot-left'])
        width = number(svg.attrib['data-plot-width'])
        require(minimum == 0, 'bars must start at zero')
        if maximum <= 0 or width <= 0:
            raise ValueError('axis maximum and plot width must be positive')
        scale = width / maximum
        rows = svg.findall("s:g[@data-country]", NS)
        require(9 <= len(rows) <= 30, 'compact ranking must contain 9–30 rows')
        require(len(rows) == number(svg.attrib['data-row-count']), 'disclosed row count differs')
        names = [row.attrib['data-country'] for row in rows]
        require(all(name.strip() for name in names) and len(set(names)) == len(names), 'country names must be nonempty and unique')
        values = [number(row.attrib['data-value']) for row in rows]
        require(values == sorted(values, reverse=True), 'rows must be sorted descending')
        require(sum(row.get('data-focal') == 'true' for row in rows) <= 1, 'more than one focal country')
        labels = svg.findall("s:text[@data-label]", NS)
        require(len(labels) == len(rows), 'each row needs one value label')
        require(sorted(label.attrib['data-label'] for label in labels) == sorted(names), 'value labels must bind each country once')
        label_map = {label.attrib['data-label']: label for label in labels}
        last_bottom = -math.inf
        for row, value in zip(rows, values):
            name = row.attrib['data-country']
            require(0 <= value <= maximum, f'{name}: value outside axis')
            bars = row.findall("s:rect[@class='bar']", NS)
            require(len(bars) == 1, f'{name}: requires exactly one bar')
            bar = bars[0]
            close(number(bar.attrib['x']), left, f'{name}: truncated bar baseline')
            close(number(bar.attrib['width']), value * scale, f'{name}: bar length disagrees with value')
            y, height = number(bar.attrib['y']), number(bar.attrib['height'])
            require(height > 0 and y > last_bottom, f'{name}: overlapping or invalid row geometry')
            last_bottom = y + height
            label = label_map[name]
            close(number(''.join(label.itertext())), value, f'{name}: printed value differs')
            close(number(label.attrib['x']), left + value * scale + 8, f'{name}: label is not at its bar end')
            close(number(label.attrib['y']), y + height, f'{name}: value label is on another row')
            require(number(label.attrib['font-size']) >= 12, f'{name}: value label below 12px')

        ticks = svg.findall("s:text[@data-tick]", NS)
        require(len(ticks) >= 2, 'axis needs at least two bound ticks')
        tick_values = [number(tick.attrib['data-tick']) for tick in ticks]
        require(0 in tick_values and maximum in tick_values, 'axis must label zero and its maximum')
        for tick, value in zip(ticks, tick_values):
            close(number(''.join(tick.itertext())), value, 'printed tick differs')
            close(number(tick.attrib['x']), left + value * scale, 'tick uses a different scale')

        benchmarks = svg.findall("s:line[@data-benchmark]", NS)
        require(len(benchmarks) <= 2, 'more than two benchmarks')
        require(len({b.attrib['data-benchmark'] for b in benchmarks}) == len(benchmarks), 'duplicate benchmark')
        for benchmark in benchmarks:
            kind, value = benchmark.attrib['data-benchmark'], number(benchmark.attrib['data-value'])
            require(0 <= value <= maximum, f'{kind}: benchmark outside axis')
            for coord in ('x1', 'x2'):
                close(number(benchmark.attrib[coord]), left + value * scale, f'{kind}: shifted benchmark')
            if kind == 'median':
                close(value, statistics.median(values), 'median does not match the shown population')
        return errors
    except (ValueError, KeyError, IndexError, ET.ParseError) as error:
        return errors + [f'invalid ranking: {error}']


def signature(source: str) -> tuple:
    svg = svg_root(source)
    return (tuple((row.get('data-country'), row.get('data-value'), row.get('data-focal'))
                  for row in svg.findall("s:g[@data-country]", NS)),
            tuple((line.get('data-benchmark'), line.get('data-value'))
                  for line in svg.findall("s:line[@data-benchmark]", NS)))


def main() -> int:
    files = [Path(arg) for arg in sys.argv[1:]] or list(VARIANTS)
    errors, signatures = [], []
    for path in files:
        try:
            source = path.read_text(encoding='utf-8')
            findings = verify(source)
            errors.extend(f'{path.name}: {finding}' for finding in findings)
            if not findings:
                signatures.append(signature(source))
        except OSError as error:
            errors.append(f'{path}: {error}')
    if not sys.argv[1:] and len(set(signatures)) > 1:
        errors.append('variant data, ordering, emphasis, or benchmarks differ')
    print('\n'.join(errors) if errors else f'OK compact ranking: {len(files)} files, scales, values, ordering, median, and benchmarks')
    return int(bool(errors))


if __name__ == '__main__':
    sys.exit(main())
