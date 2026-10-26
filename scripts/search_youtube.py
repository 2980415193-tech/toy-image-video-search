"""Search-only yt-dlp wrapper: emits candidates, never downloads media."""
import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--query', required=True)
    p.add_argument('--limit', type=int, default=5, choices=range(1, 21))
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    exe = shutil.which('yt-dlp')
    runner = [exe] if exe else None
    if not runner:
        for name in ('yt-dlp.exe', 'yt-dlp'):
            local = Path.home() / '.local/bin' / name
            if local.is_file():
                runner = [str(local)]
                break
    if not runner and importlib.util.find_spec('yt_dlp'):
        runner = [sys.executable, '-m', 'yt_dlp']
    if not runner:
        p.error('yt-dlp missing; install using python -m pip install yt-dlp or uv tool install yt-dlp')
    cmd = runner + ['--ignore-config', '--flat-playlist', '--skip-download',
           '--dump-single-json', '--socket-timeout', '15', '--retries', '0',
           '--extractor-retries', '0', '--no-warnings', '--',
           f'ytsearch{a.limit}:{a.query}']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding='utf-8', errors='replace', timeout=55)
        if result.returncode:
            raise RuntimeError(result.stderr.strip()[-1200:])
        raw = json.loads(result.stdout)
        rows, seen = [], set()
        for item in raw.get('entries') or []:
            if not isinstance(item, dict):
                continue
            vid = item.get('id', '')
            if not re.fullmatch(r'[A-Za-z0-9_-]{11}', vid) or vid in seen:
                continue
            seen.add(vid)
            rows.append({'platform': 'YouTube', 'title': item.get('title'),
                         'url': f'https://www.youtube.com/watch?v={vid}',
                         'channel': item.get('channel') or item.get('uploader'),
                         'duration_seconds': item.get('duration'),
                         'view_count': item.get('view_count'),
                         'match': '待核验', 'verification': 'search_metadata_only'})
        payload = {'status': 'ok' if rows else 'empty', 'query': a.query,
                   'results': rows}
    except (OSError, RuntimeError, subprocess.TimeoutExpired, ValueError) as e:
        payload = {'status': 'error', 'query': a.query, 'error': str(e),
                   'results': [], 'fallback': 'Use web search: site:youtube.com/watch ' + a.query}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status': payload['status'], 'count': len(payload['results']),
                      'output': str(a.output.resolve())}, ensure_ascii=False))
    return 1 if payload['status'] == 'error' else 0


if __name__ == '__main__':
    sys.exit(main())
