# One Day on Earth — Friday 20 November 2026

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/tacinbau/news-image-20261120-r2/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/tacinbau/news-image-20261120-r2/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

**The world in one page: 40 stories, 7 regions — Friday 20 November 2026.**

![One Day on Earth — Friday 20 November 2026](entry.png)

## What it is

A one-page newspaper front page that sums up Friday 20 November 2026 in a
single 1024×1024 image. Every story happened, or was first reported, on that
day — checked against wire reporting (Reuters, AP, BBC, Al Jazeera, IMD,
Xinhua, PTI, Sky News, UKMTO). Counts are officials' figures, as reported,
and every story names its source beside it.

## Inside the page

- **The Day in Numbers** — 6 key figures: 400 drones over Ukraine, 372,000
  people moved to shelters before Cyclone Akvan, Taiex −6.2%, S&P 500 −3.7%,
  100,000 youth visas a year in the UK–EU deal, Senate vote 62–33.
- **3 illustrated lead stories** — Russian missiles hit three Kyiv bridges;
  Cyclone Akvan comes ashore in eastern India; the AI sell-off sinks Asia's
  stock markets. All three pictures are original drawings, made in code.
- **Markets at the Close** — Friday's closes: Taiex −6.2%, Kospi −5.2%,
  Nikkei −5.1%, Hang Seng −1.9%, S&P 500 −3.7%, Nasdaq −5.3%, Sensex +1.1%.
- **The Day as It Happened** — a 5-point timeline, 01:25 Kyiv to 21:00 New York.
- **12 feature stories** — Poland, Europe's Russia talks, the UK–EU reset deal,
  Myanmar's rejection of the ICJ genocide ruling, Anthropic's day-two slide,
  COP31 into overtime, the Riyadh strike, the Crimea Bridge, the Hormuz tanker,
  Kenya's Ebola countdown, the US Senate vote, the Haiti raid.
- **Where It Happened** — a stylised world map with numbered pins for stories 1–15.
- **Quote of the Day** — “Putin is a killer.” — Volodymyr Zelenskyy.
- **Also on Friday** — 25 more stories, numbered 16–40.
- **Date Check** — what was deliberately left out because it happened on
  Thursday 19 November: the ICJ verdict, Anthropic's debut, the Shenzhen
  declaration, the GTA VI launch.

## Generate it

```bash
python3 main.py   # writes entry.png (1024×1024, < 1 MiB)
```

`main.py` uses only the Python standard library and Pillow, makes no network
calls, uses no randomness and no clock — running it twice produces a
byte-identical `entry.png` (verified: same MD5 on repeated runs). The build
fails loudly if any text would overflow its box or be silently truncated.

## Files

| File | What it is |
| --- | --- |
| `main.py` | The generator — draws the whole page with Pillow |
| `entry.png` | The entry image, 1024×1024 |
| `prompt.txt` | The user's brief for this entry, verbatim |
| `LICENSE` | MIT |

## License

MIT — see [LICENSE](LICENSE).
