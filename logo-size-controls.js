(function(){
  const key='ume-header-logo-sizes-v1', defaults=[220,190];
  const ids=['logoPcSize','logoMobileSize'];
  let values=defaults.slice();
  try{const saved=JSON.parse(localStorage.getItem(key));if(Array.isArray(saved)&&saved.length===2&&saved.every(n=>Number.isFinite(n)))values=saved.map((n,i)=>Math.min(i===0?480:360,Math.max(i===0?100:90,n)));}catch(e){}
  const inputs=ids.map(id=>document.getElementById(id));
  function apply(){const vals=inputs.map(el=>Number(el.value));
    document.documentElement.style.setProperty('--ume-logo-pc',vals[0]+'px');
    document.documentElement.style.setProperty('--ume-logo-mobile',vals[1]+'px');
    document.getElementById('logoPcOut').textContent=vals[0]+'px';
    document.getElementById('logoMobileOut').textContent=vals[1]+'px';
    try{localStorage.setItem(key,JSON.stringify(vals));}catch(e){}
  }
  inputs.forEach((el,i)=>{el.value=values[i];el.addEventListener('input',apply);});
  document.getElementById('logoSizeReset').addEventListener('click',()=>{inputs.forEach((el,i)=>el.value=defaults[i]);apply();});
  apply();
})();
