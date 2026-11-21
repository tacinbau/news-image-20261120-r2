[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/tacinbau/news-image-20261120-r2/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/tacinbau/news-image-20261120-r2/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

# The World in One Day — Friday 20 November 2026

**78 stories · 15 regions · one 1024×1024 front page, drawn entirely in code.**

## What this is

One image that sums up Friday 20 November 2026 in world news. Every story on
the page is dated that day — nothing from 19, 21 or 22 November.

- **Masthead** — date, story/region counts, bounty.
- **3 original hero panels, drawn with PIL** (no photos): Kyiv's Dnipro bridges
  hit in the overnight barrage; Wall Street's Red Friday rout; COP31's final
  day in Antalya.
- **World map** — stylised continents with 12 numbered pins (numbers = story
  numbers on the page).
- **Market strip** — the day's closes: Nasdaq −5.2%, S&P 500 −3.7%, Dow −1.9%,
  Nikkei −4.5%, Kospi −4.7%, Nvidia −14%, Anthropic −9% on day two,
  Bitcoin ~$59,000, gold $3,540, WTI $84.10, VIX ~36, 10-year 4.94%.
- **78 stories in 3 columns × 26 rows**, each with its number and a colour-coded
  region tag: Europe 9, Ukraine War 5, Asia-Pacific 6, South Asia 6,
  Middle East & Gulf 6, Africa 4, North America 8, Latin America & Caribbean 5,
  Oceania 3, Markets & Economy 9, Tech & AI 3, Climate & Energy 3,
  Science & Space 2, Sport 6, Culture & Society 3.
- **Region tally**, **UTC timeline** (~ session times), **Quote of the Day**
  ("A tremendous tax" — Donald Trump, White House briefing, 20 Nov 2026) and a
  **DATE CHECK** box naming what was excluded.

## DATE CHECK — why some big stories are NOT here

The following were checked and deliberately excluded because they are dated
**19 November 2026**, not 20 November: the ICJ ruling that Myanmar committed
genocide against the Rohingya; the Trump–Xi–Putin summit and joint declaration
in Shenzhen; Anthropic's first day of trading (ANT debut); the drone hit on
the Dutch embassy in Kyiv. No 21/22 November items are included either. The
stories that do appear are the 20 November developments themselves — the Kyiv
barrage and its aftermath, the second day of Anthropic trading, the EU–UK
summit, COP31's scheduled final day.

## How to reproduce

```bash
python3 main.py   # writes entry.png (1024x1024, RGB)
```

Python standard library + Pillow only. No network, no clock, no unseeded
randomness — running it twice produces a byte-identical PNG (same md5).

## Sources

Reuters, AP, Investopedia, IANS, UNFCCC, Open Chronicle, Zacks — wires of
20 November 2026, checked 21 November 2026.

## Licence

MIT — see [LICENSE](LICENSE).
