# Compact ranked bars

Use this **bar-chart variant** for a complete country ranking, league table, or benchmark comparison with 9–30 categories, one value per row, and at most two reference lines. It overrides the standard eight-bar limit, not the limits of other diagram types. Do not reduce an EU comparison to a top eight when the user asks for all 27 countries.

## Layout

- Use one horizontal plot, sorted by value descending unless the subject calls for another explicit order. Equal values retain the source order. Omit row numbers and obvious column headings: country names and bar lengths explain the ordering. A claimed rank uses ties correctly.
- Compact example: `viewBox="0 0 760 648"`, 27 rows at 16px pitch, 8px bars, 12px Geist labels and values. The first row centre is y=112; the last is y=528. Label gutter ends at x=132, plot starts at x=148, plot width=560, domain=0–70. Reserve space beyond the longest bar for its value.
- Keep labels at 12px at the delivered size. On narrow screens, preserve the diagram width in a horizontally scrollable, keyboard-focusable region; do not shrink the entire ranking into illegible text. All rows remain present, with no internal vertical scrolling. Grow height with row count; use 20px pitch if labels need more air. Above 30, use aligned panels with the same scale and disclose the split.
- Keep full country names, one number beside each bar, sparse vertical gridlines and a clear zero baseline. Omit flags, cards per country, decorative textures, and repeated units on every axis label.
- One focal country: accent bar and bold name/value, without a tinted row background. All other bars use the same muted treatment. Title: one supported finding, in Instrument Serif. Numerical labels use Geist with tabular figures.
- Default to no benchmarks or legend. Only add reference lines when requested or essential to the comparison, with up to two keys in a separate strip above the plot. Use ink dashed for one and muted dotted for the other, with matching swatches and explicit names/values. These are quantitative reference lines, not node connectors. Paint them above the bars but below value labels; paper masks behind end labels may interrupt a line locally. Never shift a benchmark away from its value to create space.
- Keep the metric, unit, ordering/population, and provenance inside the SVG so exports retain meaning. A full editorial variant adds a short interpretation/method note below the same chart; it does not enlarge the rows or remove countries.

## Numerical contract

- Bars begin at zero. Pick one finite positive axis maximum that includes every value and benchmark. `width = plot_width * value / axis_max`; benchmark `x = plot_left + plot_width * benchmark / axis_max`. Layout spacing uses the 4px grid; **data-derived widths and positions are exempt**. Rounding marks to the grid changes their values.
- This compact variant assumes nonnegative values in one unit. Negative values need a diverging bar layout; missing values need a visibly disclosed row, never a zero-length imputation. Counts and ranks must refer to the disclosed population.
- A median is computed from the complete unrounded series when available. If only rounded or image-transcribed values exist, disclose that basis. A weighted EU figure is a supplied aggregate with its own denominator/weights; never substitute the unweighted mean of country percentages.
- Distinguish a country's allocation share from its share of the whole EU budget. Do not turn “highest on this measure” into a claim about performance or desirability.
- The shipped example transcribes the user's screenshot: 27 countries, Denmark 65.5%. It omits the screenshot's median and EU-weighted references to keep the ranking simple. It demonstrates layout, not independently verified budget statistics. Its source note must stay visible when reusing that data; replace the figures and provenance together for production use.

## Examples and checks

- [Minimal light](../assets/example-bar-ranking.html)
- [Minimal dark](../assets/example-bar-ranking-dark.html)
- [Full editorial](../assets/example-bar-ranking-full.html)

From a repository checkout, run `python scripts/verify-bar-ranking.py` for the shipped examples: common scale, bar widths, printed values, ordering, and variant parity (plus median/benchmark positions when present). Use the skin and rendered-layout checks too; numeric consistency alone does not prove source accuracy or legibility.
