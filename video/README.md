# Agentic Warranty Intelligence: product video

Timed to the voiceover script, with the voiceover lines as captions. These are review captions only; the final voiceover recording comes later.

| File | What it is |
| --- | --- |
| `awi-video.html` | The video. Open it in a browser and press space to play. Arrow keys jump between beats, C turns captions on and off, H hides the controls. |
| `voiceover.md` | The voiceover script, as the video plays it. |
| `cue-sheet.md` | Start time and length of every voiceover line. Use it to pace the recording. |
| `player.template.html` | Edit beats 1 to 3 and 10, the script and the timing here. |
| `source/` | The two pages behind beats 4 to 9: the system overview and the frames page. |
| `build.py` | Run `python3 build.py` after any edit to rebuild `awi-video.html`. |
| `music/score.py` | Original temp score, synthesised from scratch, so no licence is needed. Run `python3 music/score.py` after `node render.cjs` so the music follows any retiming. |
| `render.cjs` | Run `node render.cjs` to export `out/awi-video.mp4`. Add `--no-captions` for a clean cut, or `--stills` for one image per line. |

## Beat map

| Beat | Screen |
| --- | --- |
| 1 | The team's six problems, then four impact cards with sourced figures |
| 2 | A warranty system report: every issue reported, none fixed |
| 3 | Title card |
| 4 | System overview shown in full; the source of truth lights up on its line |
| Transition | "Here is how it works": the four stages, leading into the claims hub. New voiceover line. |
| 5 to 9 | Frames page steps on the left; animated app screens on the right (claims hub, plant, procurement, finance, decisions) |
| 10 | Overview, all lit, then data sources lit; four outcome tiles with sourced industry figures; ask for a demo |

## Voiceover

The recorded read is `vo/voiceover.mp3`. `vo/align.py` matches each line to it using the pauses (no speech recognition), and the video takes its timing from `vo/alignment.json`. To rebuild the final video after any change:

    python3 build.py
    node render.cjs --stills        # writes the schedule and timeline
    python3 music/score.py
    python3 vo/mix.py               # out/final-mix.wav
    node render.cjs --no-captions   # out/awi-video-clean.mp4
    ffmpeg -i out/awi-video-clean.mp4 -i out/final-mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest out/awi-video-final.mp4

For a new recording, replace `vo/voiceover.mp3`, run `python3 vo/align.py`, then the steps above.

## Timing without a recording

Timing comes from a word-count estimate. To lock a line to the real read, set `dur` (in seconds) on its cue in the `BEATS` list in `player.template.html`, then rebuild and re-export. The app screens in beats 5 to 9 are templates (`app-f5` to `app-f9`) in `player.template.html`. Their animation keys are scheduled in the same `BEATS` list. The app data is demo data: real OEM names, invented claims, amounts, people and suppliers.

## Figures on screen

Industry figures, not client results. Check each before the pitch, or swap in the client's own baseline.

| Slide | Figure | Source |
| --- | --- | --- |
| Beat 1 | $57.9B in warranty claims paid by carmakers worldwide in 2024, up 18% | [Warranty Week, Oct 2025](https://www.warrantyweek.com/archive/ww20251030.html) |
| Beat 1 | $1.9B recovered by GM from LG on the Bolt recall | [GM 10-Q](https://www.sec.gov/Archives/edgar/data/1467858/000146785822000094/gm-20220630.htm), [CNBC](https://www.cnbc.com/amp/2021/10/12/lg-chem-to-pay-up-to-1point9-billion-to-gm-over-bolt-ev-battery-fires.html) |
| Beat 1 | 29.3M US vehicles recalled in 2024 | [NHTSA](https://www.nhtsa.gov/press-releases/consumer-alert-change-your-clocks-check-safety-recalls) |
| Beat 1 | 3-15% of warranty cost from invalid or fraudulent claims | Kurvinen et al. (2016), citing Arnum (2015); secondhand |
| Beat 10 | 13 months earlier warning on quality issues | Deloitte case study with Daimler; reported, not audited |
| Beat 10 | 5-10% warranty cost cut expected by 58% of surveyed leaders | [McKinsey](https://www.mckinsey.com/industries/automotive-and-assembly/our-insights/when-warranty-costs-rival-r-and-d-spend-remaking-vehicle-quality-with-ai) |
| Beat 10 | 95% of Bolt recall cost recovered ($1.9B of $2.0B) | GM filings, as above |
| Beat 10 | 18% of automakers use AI in production to predict quality issues | McKinsey, as above |

## Music

`music/score.py` writes `music/score.wav`, an original temp score timed to the beats: B minor tension under the problem, a lift into D major on the reveal, a pulse that builds through the walkthrough, a drop under beat 9 and a full close at 100 BPM. To preview it with the picture:

    ffmpeg -i out/awi-video.mp4 -i music/score.wav -filter_complex "[1:a]loudnorm=I=-18[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -shortest out/awi-video-music.mp4

Under the voiceover, sit the music about 15 dB below the voice (voice near -16 LUFS, music near -31 LUFS), or duck it to that level only while the voice speaks.
