const $ = id => document.getElementById(id);
let examples = [], active = 0;
function loadEvent(i) {
  active = i;
  const e = examples[i];
  $('message').value = e.message;
  $('trusted').checked = e.trusted !== false;
  $('sideEffect').checked = e.external_side_effect === true;
  $('approval').checked = e.requires_approval === true;
  [...$('scenarios').children].forEach((node, j) => node.classList.toggle('active', i === j));
  $('output').hidden = true; $('empty').hidden = false; $('error').textContent = '';
}
async function init() {
  try {
    const res = await fetch('/api/examples');
    if (!res.ok) throw Error('Could not load examples');
    examples = await res.json();
    const labels = ['Network timeout', 'Payment approval', 'Untrusted prompt', 'Verified completion'];
    examples.forEach((e,i) => {
      const b = document.createElement('button');
      b.className = 'scenario'; b.textContent = labels[i] || e.id;
      b.addEventListener('click', () => loadEvent(i));
      $('scenarios').append(b);
    });
    loadEvent(0);
  } catch (err) { $('error').textContent = err.message; }
}
$('analyze').addEventListener('click', async () => {
  $('error').textContent = ''; $('analyze').disabled = true;
  try {
    const event = {id: examples[active]?.id || 'custom', message: $('message').value,
      trusted: $('trusted').checked, external_side_effect: $('sideEffect').checked,
      requires_approval: $('approval').checked};
    const res = await fetch('/api/analyze', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(event)});
    const data = await res.json();
    if (!res.ok) throw Error(data.error || 'Analysis failed');
    $('state').textContent = data.suggested_state.toUpperCase();
    $('state').className = 'state '+data.suggested_state;
    $('reason').textContent = data.reason.replaceAll('_',' ');
    $('model').textContent = data.model.label.toUpperCase();
    $('confidence').textContent = (data.model.confidence*100).toFixed(1)+'%';
    $('executed').textContent = String(data.executed_actions);
    $('alternatives').replaceChildren();
    data.model.alternatives.forEach(a => {
      const row = document.createElement('div'); row.className='alternative';
      const label = document.createElement('span'); label.textContent=a.label;
      const track = document.createElement('div'); track.className='track';
      const fill = document.createElement('div'); fill.className='fill'; fill.style.width=(a.probability*100)+'%';
      track.append(fill);
      const pct = document.createElement('span'); pct.textContent=(a.probability*100).toFixed(1)+'%';
      row.append(label,track,pct); $('alternatives').append(row);
    });
    $('empty').hidden=true; $('output').hidden=false;
  } catch(err) { $('error').textContent=err.message; } finally { $('analyze').disabled=false; }
});
init();