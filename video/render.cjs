// Export awi-video.html to MP4, frame by frame, and write the cue sheet.
//   node render.cjs                      -> out/awi-video.mp4 (captions on)
//   node render.cjs --no-captions        -> out/awi-video-clean.mp4
//   node render.cjs --stills             -> out/stills/*.png, one per cue, no video
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const FPS = 30;
const args = process.argv.slice(2);
const captions = !args.includes('--no-captions');
const stillsOnly = args.includes('--stills');

(async () => {
  const outDir = path.join(__dirname, 'out');
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  const url = 'file://' + path.join(__dirname, 'awi-video.html') + '?render=1&cc=' + (captions ? 1 : 0);
  await page.goto(url);
  await page.evaluate(() => document.fonts.ready);
  const duration = await page.evaluate(() => window.AWV.duration);
  const cues = await page.evaluate(() => window.AWV.cues);

  const fmt = s => `${Math.floor(s / 60)}:${(s % 60).toFixed(1).padStart(4, '0')}`;
  const sheet = ['# Cue sheet', '', `Runtime ${fmt(duration)}. Start times follow the recorded voiceover (vo/alignment.json) when present, otherwise a word-count estimate.`, '',
    '| Start | Length | Beat | Line |', '| --- | --- | --- | --- |',
    ...cues.map(c => `| ${fmt(c.start)} | ${c.dur.toFixed(1)}s | ${c.beat} | ${c.text} |`), ''];
  fs.writeFileSync(path.join(__dirname, 'cue-sheet.md'), sheet.join('\n'));
  // Beat start times, for music/score.py.
  const beats = {};
  cues.forEach(c => { if (!(c.beat in beats)) beats[c.beat] = c.start; });
  fs.writeFileSync(path.join(__dirname, 'music', 'timeline.json'), JSON.stringify({ duration, beats }, null, 2));
  // Cue schedule, for vo/mix.py.
  fs.writeFileSync(path.join(__dirname, 'vo', 'schedule.json'), JSON.stringify({ duration, cues }, null, 1));

  if (stillsOnly) {
    const dir = path.join(outDir, 'stills');
    fs.mkdirSync(dir, { recursive: true });
    for (let i = 0; i < cues.length; i++) {
      const c = cues[i];
      await page.evaluate(t => window.AWV.seek(t), c.start + c.dur - 0.35);
      await page.screenshot({ path: path.join(dir, `cue-${String(i + 1).padStart(2, '0')}.png`) });
    }
    await browser.close();
    console.log(`wrote ${cues.length} stills`);
    return;
  }

  const file = path.join(outDir, captions ? 'awi-video.mp4' : 'awi-video-clean.mp4');
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', file],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  const total = Math.ceil(duration * FPS);
  for (let f = 0; f <= total; f++) {
    await page.evaluate(t => window.AWV.seek(t), f / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % (FPS * 10) === 0) console.log(`${fmt(f / FPS)} / ${fmt(duration)}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('wrote ' + file);
})();
