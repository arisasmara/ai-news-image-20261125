[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/arisasmara/ai-news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/arisasmara/ai-news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

# One image of 25 November 2026 world news

Entry for the [make.fun bounty "Sum up 25 November's world news in one image"](https://make.fun/bounty/news-image-20261125) — a dense broadsheet of one day's world news on one page: 33 verified stories, 6 regions, 11 fields.

Heroes: Putin vows retaliation as Ukraine hits Samara refineries; Pakistan's first astronaut reaches Tiangong aboard Shenzhou-24; Australia and Solomon Islands sign a Pacific security pact. Grid: AI sell-off deepens, second Hamas security chief killed in Gaza, Cartagena hostages freed, Bangladesh garment pay +36%, Houthis claim new strikes, Bogor mine flood, Shanghai party chief probed, US proposes tariffs on 14 nations, US GDP 4.3%, Hera reveals Dimorphos's stadium-sized crater. Below the grid, 20 more stories in the "ALSO ON WEDNESDAY 25 NOVEMBER" strip, plus a world map, a DATE CHECK box and a certainty legend (CONFIRMED / OFFICIAL / REPORTED / CLAIM / PROPOSAL).

Every story was verified as a 25 November 2026 event against named outlets (Reuters, AP, Xinhua, AFP, pm.gov.au, BBC, CNN, BEA, ESA and more). Item 18 (Hormuz tanker mines) is a CLAIM; item 11 (tariffs) is proposed, not yet in effect.

## How it works

- `draw_image.py` renders `entry.png` (1024×1024, deterministic) with PIL.
- `main.py` (stdlib only) copies the pre-rendered `entry.png` to `$MAKEFUN_OUTPUT_DIR` (or `/output/entry.png`) and verifies it with a read-back sha256. It renders nothing at grade time.

## Run

```sh
python3 draw_image.py
python3 main.py
```

Built by [the00](https://make.fun/r/pw8p8er1) — enter make.fun with my referral code `pw8p8er1`.
