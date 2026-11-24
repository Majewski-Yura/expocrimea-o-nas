(() => {
 const grid=document.querySelector('#news-grid'), more=document.querySelector('#news-more');
 if(!grid||!more)return;
 const cards=[...grid.children], box=document.querySelector('.chips[data-for="#news-grid"]'), count=document.querySelector('.nl__count');
 let category='all', limit=24;
 const render=()=>{
  const matches=cards.filter(card=>category==='all'||card.dataset.f===category);
  cards.forEach(card=>{card.hidden=true;card.classList.remove('pop','rv');card.classList.add('in')});
  matches.slice(0,limit).forEach(card=>{card.hidden=false});
  more.hidden=limit>=matches.length;
  count.textContent=`Показано ${Math.min(limit,matches.length)} из ${matches.length}`;
 };
 box.addEventListener('click',e=>{const button=e.target.closest('.chip');if(!button)return;category=button.dataset.f;limit=24;render()});
 more.addEventListener('click',()=>{limit+=24;render()});
 render();
})();
