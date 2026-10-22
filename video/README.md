# Agentic Warranty Intelligence: product video

Timed to the voiceover script, with the voiceover lines as captions. These are review captions only; the final voiceover recording comes later.

| File | What it is |
| --- | --- |
| `awi-video.html` | The video. Open it in a browser and press space to play. Arrow keys jump between beats, C turns captions on and off, H hides the controls. |
| `cue-sheet.md` | Start time and length of every voiceover line. Use it to pace the recording. |
| `player.template.html` | Edit beats 1 to 3 and 10, the script and the timing here. |
| `source/` | The two pages behind beats 4 to 9: the system overview and the frames page. |
| `build.py` | Run `python3 build.py` after any edit to rebuild `awi-video.html`. |
| `render.cjs` | Run `node render.cjs` to export `out/awi-video.mp4`. Add `--no-captions` for a clean cut, or `--stills` for one image per line. |

## Beat map

| Beat | Screen |
| --- | --- |
| 1 | The team's six problems, then the four impact cards |
| 2 | A warranty system report: every issue reported, none fixed |
| 3 | Title card |
| 4 | System overview, lit section by section: agents, roles, then the source of truth |
| 5 to 9 | Frames page: claims hub, plant, procurement, finance, who decides |
| 10 | Overview, all lit, then data sources lit; four outcome tiles; ask for a demo |

## After the voiceover is recorded

Timing comes from a word-count estimate. To lock a line to the real read, set `dur` (in seconds) on its cue in the `BEATS` list in `player.template.html`, then rebuild and re-export. The APP CAPTURE boxes in beats 5 to 9 are still placeholders for screen recordings.
