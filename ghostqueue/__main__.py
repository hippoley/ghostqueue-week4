import argparse, json, sys
from .core import triage

def main():
    p=argparse.ArgumentParser(description='GhostQueue: offline AI triage for abandoned jobs (advisory only)')
    p.add_argument('events',help='JSON array of events or JSONL file')
    args=p.parse_args()
    with open(args.events,encoding='utf-8') as f: raw=f.read()
    try: events=json.loads(raw)
    except json.JSONDecodeError: events=[json.loads(line) for line in raw.splitlines() if line.strip()]
    if isinstance(events,dict): events=[events]
    if not isinstance(events,list):
        p.error('input must be a JSON object, array, or JSONL records')
    for index,event in enumerate(events,1):
        try:
            print(json.dumps(triage(event),ensure_ascii=False))
        except (ValueError, TypeError, KeyError) as exc:
            print(f'Invalid event #{index}: {exc}', file=sys.stderr)
            return 2
if __name__=='__main__':sys.exit(main())
