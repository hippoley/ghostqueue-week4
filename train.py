"""Train a transparent local text model on synthetic task-event examples.
Install scikit-learn for training only; inference uses Python standard library.
"""
import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

SAMPLES={
"retry":["worker timeout while reading file, temporary network timeout","rate limit hit 429, retry after cooldown","upstream unavailable 503, transient service error","temporary connection reset during task, retry with backoff","job interrupted by transient socket timeout","worker crashed before ack, recover and retry safely","network read timed out while fetching record","remote server returned 502 bad gateway transient"],
"review":["payment approval missing, requires human authorization","uncertain recipient identity, ask human to review","ambiguous task owner, manual decision required","requested deletion requires explicit approval","insufficient permission to publish the report","new vendor bank details need manual verification","user consent missing for outbound message","unknown destination, stop and request approval"],
"quarantine":["untrusted document says ignore policy and exfiltrate secrets","prompt injection detected in tool response, quarantine","invalid payload schema with malicious instruction","repeated checksum mismatch indicates corrupted input","unexpected instruction to reveal private tokens","payload contains forged system message and credential request","untrusted content attempts to override developer instructions","malformed event and signature mismatch, isolate"],
"complete":["job completed with verified receipt and durable ack","task succeeded, checksum matches, record reconciled","operation finished, all expected outputs verified","workflow finalized with confirmed idempotency key","report saved successfully and validation passed","result committed and execution receipt persisted","queue message processed with success acknowledgment","output verified, no pending work remains"]
}
def main():
    texts=[x for group in SAMPLES.values() for x in group]
    labels=[label for label,group in SAMPLES.items() for _ in group]
    vec=TfidfVectorizer(ngram_range=(1,2),lowercase=True)
    X=vec.fit_transform(texts)
    model=LogisticRegression(max_iter=1000,C=5,random_state=7)
    model.fit(X,labels)
    export={"model_type":"tfidf_multinomial_logistic_regression","training_data":"synthetic_examples_only","classes":list(model.classes_),"vocabulary":{k:int(v) for k,v in vec.vocabulary_.items()},"idf":[round(float(x),9) for x in vec.idf_],"weights":[[round(float(v),9) for v in row] for row in model.coef_],"intercepts":[round(float(x),9) for x in model.intercept_],"token_pattern":r"(?u)\b\w\w+\b"}
    path=Path(__file__).parent/'ghostqueue'/'weights.json'
    path.write_text(json.dumps(export,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({"training_examples":len(texts),"training_accuracy":round(float(accuracy_score(labels,model.predict(X))),3),"weights":str(path)}))
if __name__=='__main__':main()
