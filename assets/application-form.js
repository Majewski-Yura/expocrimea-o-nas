(() => {
 if(!window.HTMLDialogElement)return;
 const base=new URL('../',document.currentScript.src);
 const dlg=document.createElement('dialog');dlg.className='pop-f';
 dlg.innerHTML=`
    <form class="ct-form" data-application-form>
      <button class="pop-f__x" type="button" aria-label="Закрыть"><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></svg></button>
      <h2>Напишите нам</h2>
      <p>Ответим в рабочее время. Письмо откроется в вашей почтовой программе.</p>
      <label><span>Имя</span><input name="name" required autocomplete="name"></label>
      <label><span>Телефон</span><input name="phone" type="tel" required autocomplete="tel"></label>
      <label><span>Сообщение</span><textarea name="msg" rows="4"></textarea></label>
      <label class="ct-form__ok"><input type="checkbox" required> <span>Даю согласие на <a href="${base.href}politika/index.html" target="_blank">обработку персональных данных</a></span></label>
      <button class="btn" type="submit">Отправить</button>
    </form>`;
 document.body.append(dlg);
 const form=dlg.querySelector('form');
 const title=dlg.querySelector('h2');
 const selector='[data-join-purpose],a.btn[href="#apply"],a.btn[href="#join"],a.btn[href="#contacts"],a.btn[href$="#form"],.fab--chat';
 document.addEventListener('click',e=>{
   const link=e.target.closest(selector);if(!link)return;
   e.preventDefault();
   const label=link.textContent.trim().replace(/\s+/g,' ')||link.getAttribute('aria-label')||'Напишите нам';
   let purpose=link.dataset.joinPurpose;
   if(!purpose){
     if(/участ/i.test(label))purpose='Участие в мероприятии';
     else if(/посет/i.test(label))purpose='Посещение мероприятия';
     else if(/партн/i.test(label))purpose='Партнёрство';
     else if(/звонок/i.test(label))purpose='Обратный звонок';
     else purpose=label;
   }
   const heading=document.querySelector('.hero__title');
   const page=heading?(heading.textContent.trim().replace(/\s+/g,' ')||heading.getAttribute('aria-label')||document.title):document.title;
   title.textContent=purpose==='Обратный звонок'?purpose:'Оставить заявку';
   dlg.setAttribute('aria-label',title.textContent);
   form.elements.msg.value=purpose+' — '+page;
   const header=document.querySelector('.header');if(header)header.classList.remove('is-open');
   document.body.classList.remove('menu-open');
   const burger=document.querySelector('.burger');if(burger)burger.setAttribute('aria-expanded','false');
   dlg.showModal();form.elements.name.focus({preventScroll:true});
 });
 dlg.querySelector('.pop-f__x').addEventListener('click',()=>dlg.close());
 dlg.addEventListener('click',e=>{if(e.target===dlg)dlg.close()});
 form.addEventListener('submit',e=>{
   e.preventDefault();if(!form.reportValidity())return;
   const body='Имя: '+form.elements.name.value.trim()+'\nТелефон: '+form.elements.phone.value.trim()+'\n\n'+form.elements.msg.value.trim();
   location.href='mailto:info@expocrimea.com?subject='+encodeURIComponent('Заявка с сайта ЭКСПОКРЫМ')+'&body='+encodeURIComponent(body);
 });
})();
