[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/tacinbau/news-image-20261120-r2/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/tacinbau/news-image-20261120-r2/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

# The World in One Day — Friday 20 November 2026

One 1024×1024 newspaper image summing up Friday 20 November 2026:
**58 stories across 10 regions** — Europe, East Asia, South Asia, Southeast
Asia, the Middle East, Africa, North America, Latin America, Oceania, and
Global — every one dated to that Friday.

## What's on the page

- **The day in UTC** — a timeline from the Kyiv bridge strikes (00:00) to the
  Nasdaq close (-5.3%, 21:00).
- **By the numbers** — 3 bridges hit, 300,000+ people moved before Cyclone
  Akvan, 111 missiles + 404 drones, 100,000 youth visas a year in the UK–EU
  deal, Taipei -6.2%, Nvidia -14%.
- **Three hero stories** with original PIL-drawn art: the Kyiv bridges at
  night, Cyclone Akvan's landfall near Gopalpur, and the AI sell-off chart.
- **Ten more stories** (4–13) with their own drawn icons: the UK–EU reset,
  COP31's last day with no deal, the Kh-101 in Poland, Iraq's Jurf al-Sakhar
  operation, Italy's general strike, Japan's inflation, Korea's impeachment
  move, Kenya's first oil well, Bukele's third-term filing, and Phillips' 118.
- **Markets at close** — Taipei, Seoul, Tokyo, Nasdaq, S&P 500, Dow, Brent,
  gold.
- **Where it happened** — a world map with numbered pins for stories 1–13,
  plus 45 more stories in the index.
- **Quote of the day** — "It's a meltdown." (Arun Sundaram, CFRA Research,
  on the AI sell-off).
- **Date check** — items from other dates (Anthropic's 19 Nov IPO debut, the
  EU big-tech tax plan dated 21 Nov, COP31's next draft, the ATP Finals final)
  are listed as excluded, not counted as Friday stories.

## Facts

Every story happened, or was first reported, on Friday 20 November 2026, and
is sourced beside the story (BBC, Reuters, CNBC, CNN, AP, AFP, IMD, Xinhua,
Anadolu, RTE, and others). No numbers, names, or dates are invented.

## Build

```sh
python3 main.py   # writes entry.png (1024x1024, RGB)
```

Python standard library + Pillow only. All artwork is drawn with PIL — no
photographs or downloaded images. The build is deterministic: running it
twice produces a byte-identical `entry.png`.

## License

MIT — see [LICENSE](LICENSE).
