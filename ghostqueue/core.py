"""Dependency-free local inference over openly published model weights.
No tool execution, network calls, or credential access is performed.
"""
import json, math, re
from collections import Counter
from pathlib import Path

WEIGHTS_PATH = Path(__file__).with_name('weights.json')
TOKEN_RE = re.compile(r'(?u)\b\w\w+\b')


def features(text, vocab, idf):
    tokens=TOKEN_RE.findall(text.lower())
    terms=tokens + [a+' '+b for a,b in zip(tokens,tokens[1:])]
    counts=Counter(terms)
    vals={}
    for term, count in counts.items():
        idx=vocab.get(term)
        if idx is not None:
            vals[idx]=count*idf[idx]
    norm=math.sqrt(sum(v*v for v in vals.values()))
    return {idx:v/norm for idx,v in vals.items()} if norm else {}


def predict(text, weights=None):
    if not isinstance(text, str):
        raise ValueError('text must be a string')
    weights = weights if weights is not None else json.loads(WEIGHTS_PATH.read_text(encoding='utf-8'))
    vals=features(text,weights['vocabulary'],weights['idf'])
    logits=[b+sum(row[i]*v for i,v in vals.items()) for row,b in zip(weights['weights'],weights['intercepts'])]
    maxlog=max(logits)
    exp=[math.exp(z-maxlog) for z in logits]
    probs=[v/sum(exp) for v in exp]
    rank=sorted(zip(weights['classes'],probs),key=lambda x:-x[1])
    return {'label':rank[0][0],'confidence':round(rank[0][1],4),'alternatives':[{"label":k,"probability":round(v,4)} for k,v in rank]}


def triage(event):
    if not isinstance(event, dict):
        raise ValueError('event must be a JSON object')
    if not isinstance(event.get('message'), str) or not event['message'].strip():
        raise ValueError('event.message must be a non-empty string')
    if len(event['message']) > 10000:
        raise ValueError('event.message exceeds 10000 characters')
    for flag in ('trusted', 'external_side_effect', 'requires_approval'):
        if flag in event and type(event[flag]) is not bool:
            raise ValueError(f'event.{flag} must be a boolean')
    if 'id' in event and (type(event['id']) not in (str, int) or (type(event['id']) is str and not event['id'].strip())):
        raise ValueError('event.id must be a string or integer')
    text=event['message']
    result=predict(text)
    action=result['label']
    reason='model_prediction'
    if event.get('trusted') is False:
        action='quarantine'; reason='hard_policy_untrusted_input'
    elif event.get('external_side_effect') or event.get('requires_approval'):
        action='review'; reason='hard_policy_human_approval'
    elif result['confidence'] < 0.55:
        action='review'; reason='model_uncertain'
    return {"event_id":event.get('id'),"suggested_state":action,"reason":reason,"model":result,"executed_actions":0}
