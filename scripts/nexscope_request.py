"""Prepare a Nexscope request; execute only after free-credit verification."""
import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ENDPOINTS = {'amazon-image': '/api/v1/tools/research/amazon/searchByImage',
             'tiktok-video': '/api/v1/tools/research/echotik/listVideo'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation', choices=ENDPOINTS)
    p.add_argument('--params', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--free-credits-confirmed', action='store_true')
    a = p.parse_args()
    params = json.loads(a.params.read_text(encoding='utf-8-sig'))
    if not isinstance(params, dict):
        p.error('Parameters must be an object')
    if a.operation == 'amazon-image':
        u = urlparse(params.get('imageUrl', ''))
        if u.scheme not in ('https', 'http') or not u.hostname:
            p.error('A public image URL is required')
        params.setdefault('amazonDomain', 'amazon.com')
        params.setdefault('aggregateByKeepaData', False)
    else:
        if not params.get('region') or not params.get('productId'):
            p.error('region and a verified TikTok productId are required')
        params.setdefault('pageSize', 10)
        params.setdefault('pageNum', 1)
        if params['pageSize'] != 10 or params['pageNum'] != 1:
            p.error('Free-first adapter is limited to the first 10 results')
    base = os.environ.get('NEXSCOPE_PROXY_BASE', 'https://api.nexscope.ai/').rstrip('/')
    if base != 'https://api.nexscope.ai':
        p.error('This adapter sends credentials only to https://api.nexscope.ai')
    url = base + ENDPOINTS[a.operation]
    if not a.free_credits_confirmed:
        result = {'status': 'plan_only', 'url': url, 'params': params,
                  'note': 'No network request. Verify account free credits before execution.'}
    else:
        key = os.environ.get('NEXSCOPE_API_KEY', '').strip()
        if not key:
            p.error('NEXSCOPE_API_KEY missing; no request sent')
        request = Request(url, data=json.dumps(params).encode('utf-8'),
                          headers={'Authorization': 'Bearer ' + key,
                                   'Content-Type': 'application/json'}, method='POST')
        try:
            with urlopen(request, timeout=45) as r:
                data = json.load(r)
            ok = isinstance(data, dict) and type(data.get('code')) is int and data['code'] == 0
            result = {'status': 'ok' if ok else 'api_error', 'response': data}
        except HTTPError as e:
            result = {'status': 'http_error', 'http_status': e.code}
        except (URLError, TimeoutError, ValueError) as e:
            result = {'status': 'error', 'error_type': type(e).__name__}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status': result['status'], 'output': str(a.output.resolve())}))
    return 0 if result['status'] in ('ok', 'plan_only') else 1


if __name__ == '__main__':
    sys.exit(main())
