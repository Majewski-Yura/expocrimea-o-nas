(() => {
 const root=document.documentElement;
 const saved=(()=>{try{return localStorage.getItem('expo-theme')}catch{return null}})();
 const query=new URLSearchParams(location.search).get('theme');
 root.dataset.theme=query==='dark'||query==='light'?query:saved==='dark'?'dark':'light';
 if(query==='dark'||query==='light'){try{localStorage.setItem('expo-theme',query)}catch{}}
 document.addEventListener('DOMContentLoaded',()=>{
  const header=document.querySelector('.header__in');if(!header)return;
  const button=document.createElement('button');button.className='theme-toggle';button.type='button';
  button.innerHTML='<svg class="theme-toggle__moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20.5 13A8.5 8.5 0 0 1 11 3.5 8.5 8.5 0 1 0 20.5 13Z"/></svg><svg class="theme-toggle__sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/></svg>';
  const update=()=>{const dark=root.dataset.theme==='dark';button.setAttribute('aria-label',dark?'Включить светлую тему':'Включить тёмную тему');button.title=button.getAttribute('aria-label');button.setAttribute('aria-pressed',String(dark))};
  button.addEventListener('click',()=>{root.dataset.theme=root.dataset.theme==='dark'?'light':'dark';try{localStorage.setItem('expo-theme',root.dataset.theme)}catch{}update()});
  header.insertBefore(button,header.querySelector('.burger'));update();
 });
})();
