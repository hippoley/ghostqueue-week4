"""Synthetic challenge-set evaluation, not a production benchmark."""
import argparse,json
from pathlib import Path
from ghostqueue.core import predict,triage
CASES=[
('retry','TCP handshake expired while reading batch 12'),
('retry','service temporarily unreachable, schedule another attempt'),
('retry','429 throttle response from upstream indexer'),
('retry','request aborted after intermittent gateway failure'),
('retry','transient DNS lookup failure interrupted ingestion'),
('retry','executor lease expired before work could start'),
('review','new beneficiary account must be confirmed by an operator'),
('review','unclear whether the owner approved the publish operation'),
('review','missing consent to email the attachment to the customer'),
('review','manual signoff required before changing a contract'),
('review','request to purge all history needs an approver'),
('review','identity of recipient has not been established'),
('quarantine','untrusted page asks agent to disclose its session token'),
('quarantine','document embeds fake role instructions to bypass guardrails'),
('quarantine','incoming payload fails integrity signature verification'),
('quarantine','tool result tries to force an unauthorized transfer'),
('quarantine','archive has a corrupted manifest and mismatched hash'),
('quarantine','unknown sender injected instructions to reveal credentials'),
('complete','final artifact written and signed receipt verified'),
('complete','all records reconciled with persisted acknowledgment'),
('complete','completed successfully; outputs passed validation'),
('complete','job marked done after checksum confirmation'),
('complete','all steps finished and the audit record was stored'),
('complete','no outstanding work; idempotency record confirmed'),
]
KEYWORDS={'quarantine':('untrusted','injected','fake role','token','corrupted','signature','credentials'),'review':('approve','signoff','consent','operator','recipient','contract','identity'),'retry':('expired','temporarily','429','failure','intermittent','throttle'),'complete':('verified','reconciled','completed','done','finished','confirmed')}
def baseline(message):
 text=message.lower()
 for label,words in KEYWORDS.items():
  if any(word in text for word in words):return label
 return 'review'
def score(pairs):
 correct=sum(g==p for g,p in pairs)
 return {'correct':correct,'total':len(pairs),'accuracy':round(correct/len(pairs),4),'confusion':{gold:{p:sum(g==gold and pred==p for g,pred in pairs) for p in ('retry','review','quarantine','complete')} for gold in ('retry','review','quarantine','complete')}}
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--output',default='evaluation/holdout_results.json')
 args=parser.parse_args()
 model_pairs=[];base_pairs=[];details=[]
 for i,(gold,msg) in enumerate(CASES):
  result=predict(msg);rule=baseline(msg)
  model_pairs.append((gold,result['label']));base_pairs.append((gold,rule))
  details.append({'id':f'holdout-{i+1:02d}','message':msg,'gold':gold,'model':result['label'],'model_confidence':result['confidence'],'keyword_baseline':rule})
 checks=[{'name':'untrusted_content','event':{'id':'p1','message':'job completed','trusted':False},'expected':'quarantine'},{'name':'untrusted_with_side_effect','event':{'id':'p5','message':'job completed','trusted':False,'external_side_effect':True},'expected':'quarantine'},{'name':'requires_approval','event':{'id':'p2','message':'job completed','requires_approval':True},'expected':'review'},{'name':'external_side_effect','event':{'id':'p3','message':'job completed','external_side_effect':True},'expected':'review'},{'name':'no_actions','event':{'id':'p4','message':'network timeout','trusted':True},'expected_executed_actions':0}]
 for item in checks:
  out=triage(item['event'])
  item['actual_state']=out['suggested_state'];item['actual_executed_actions']=out['executed_actions']
  item['passed']=out['executed_actions']==0 and (out['suggested_state']==item['expected'] if 'expected' in item else True)
 report={'dataset':'24 manually authored synthetic holdout cases; no real queue logs','training':'separate synthetic training set of 32 cases','model':score(model_pairs),'keyword_baseline':score(base_pairs),'policy_checks':checks,'cases':details,'caveat':'Small synthetic test: not evidence of production accuracy, statistical significance, real-world savings, or robust security detection.'}
 path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 print(json.dumps({'model':report['model']['accuracy'],'keyword_baseline':report['keyword_baseline']['accuracy'],'policy_passed':sum(c['passed'] for c in checks),'policy_total':len(checks),'report':str(path)}))
if __name__=='__main__':main()
