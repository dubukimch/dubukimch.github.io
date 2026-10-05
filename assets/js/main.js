'use strict';
document.documentElement.classList.add('js');
const navToggle=document.querySelector('.nav-toggle');
const nav=document.querySelector('#nav');
if(navToggle&&nav){
  navToggle.hidden=false;
  const closeNav=()=>{nav.classList.remove('open');navToggle.setAttribute('aria-expanded','false');};
  navToggle.addEventListener('click',()=>{const open=nav.classList.toggle('open');navToggle.setAttribute('aria-expanded',String(open));});
  nav.querySelectorAll('a').forEach(link=>link.addEventListener('click',closeNav));
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&nav.classList.contains('open')){closeNav();navToggle.focus();}});
}
const lightbox=document.querySelector('#lightbox');
if(lightbox){
  const image=lightbox.querySelector('img');
  const caption=lightbox.querySelector('figcaption');
  let opener;
  document.querySelectorAll('[data-lightbox]').forEach(button=>button.addEventListener('click',()=>{
    opener=button;image.src=button.dataset.lightbox;image.alt=button.dataset.caption||'프로젝트 화면';caption.textContent=button.dataset.caption||'';lightbox.showModal();
  }));
  lightbox.querySelector('.lightbox-close').addEventListener('click',()=>lightbox.close());
  lightbox.addEventListener('click',event=>{if(event.target===lightbox)lightbox.close();});
  lightbox.addEventListener('close',()=>opener?.focus());
}
