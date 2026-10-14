const $ = (selector, root=document) => root.querySelector(selector);
const $$ = (selector, root=document) => [...root.querySelectorAll(selector)];
function toast(message){const el=$("#toast");if(!el)return;el.textContent=message;el.classList.add("show");clearTimeout(window.toastTimer);window.toastTimer=setTimeout(()=>el.classList.remove("show"),2600)}
$("#mobileMenu")?.addEventListener("click",()=>$("#mainNav").classList.toggle("open"));
const path=location.pathname;
const navKey=path==="/"?"home":path==="/destinations"?"destinations":path==="/planner"?"planner":path==="/analytics"?"analytics":path==="/quiz"?"quiz":"favorites";
$(`[data-nav="${navKey}"]`)?.classList.add("active");
const imageQueries={
  "Taj Mahal":"photo-1564507592333-c60657eea523","India Gate":"photo-1597040663342-45b6af3d91a5",
  "Humayun's Tomb":"photo-1599661046827-dacff0c0f09a","Hawa Mahal":"photo-1599661046827-dacff0c0f09a",
  "Golden Temple":"photo-1609947017136-9daf32a5eb16","Gateway of India":"photo-1570168007204-dfb528c6958f",
  "Mysore Palace":"photo-1600100397608-f010d1f7a9b5","Red Fort":"photo-1587474260584-136574528ed5",
  "India":"photo-1524492412937-b28074a5d7da","default":"photo-1524492412937-b28074a5d7da"
};
function imageFor(item){
  const key=Object.keys(imageQueries).find(k=>(item.name||"").toLowerCase().includes(k.toLowerCase()));
  const photo=imageQueries[key||"default"];
  return `https://images.unsplash.com/${photo}?auto=format&fit=crop&w=700&q=78`;
}
function escapeHtml(value){return String(value??"").replace(/[&<>"']/g,ch=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]))}
function money(n){return Number(n||0)===0?"Free":`₹${Number(n||0).toLocaleString("en-IN",{maximumFractionDigits:0})}`}
function cardHtml(item, options={}){
 const saved=options.savedIds?.has(Number(item.id));
 const rating=Number(item.rating||0).toFixed(1);
 return `<article class="destination-card" data-id="${item.id}">
  <div class="card-image"><img loading="lazy" src="${imageFor(item)}" alt="${escapeHtml(item.name)}" onerror="this.style.display='none';this.parentElement.insertAdjacentHTML('afterbegin','<div class=&quot;card-placeholder&quot;>✧</div>')">
  <span class="card-tag">${escapeHtml(item.type||"Attraction")}</span>
  <button class="heart-button ${saved?'saved':''}" data-favorite="${item.id}" aria-label="Save ${escapeHtml(item.name)}">${saved?'♥':'♡'}</button></div>
  <div class="card-body"><div class="card-location">${escapeHtml([item.city,item.state].filter(Boolean).join(" · ")||"India")}</div>
  <div class="card-title-row"><h3>${escapeHtml(item.name)}</h3><span class="card-rating">★ ${rating}</span></div>
  <div class="card-meta"><span>◷ <b>${Number(item.visit_hours||0)} hrs</b></span><span>Entry <b>${money(item.entrance_fee)}</b></span></div>
  <div class="card-action"><span class="card-location">${escapeHtml(item.best_time||"Explore anytime")}</span><button data-details="${item.id}">Discover place ↗</button></div></div></article>`;
}
async function api(url,options={}){const response=await fetch(url,{headers:{"Content-Type":"application/json"},...options});if(!response.ok){let message="Something went wrong.";try{message=(await response.json()).error||message}catch(e){}throw new Error(message)}return response.json()}
document.addEventListener("click",async e=>{
 const fav=e.target.closest("[data-favorite]");
 if(fav){e.preventDefault();try{const result=await api(`/api/favorites/${fav.dataset.favorite}`,{method:"POST"});fav.classList.toggle("saved",result.saved);fav.textContent=result.saved?"♥":"♡";toast(result.saved?"Added to your saved places":"Removed from saved places");document.dispatchEvent(new CustomEvent("favoritesChanged"));}catch(err){toast(err.message)}}
 const detail=e.target.closest("[data-details]");
 if(detail){try{const item=await api(`/api/destinations/${detail.dataset.details}`);showDetail(item)}catch(err){toast(err.message)}}
});
function showDetail(item){
 const modal=$("#detailModal"),content=$("#detailContent");if(!modal||!content){location.href="/destinations";return}
 content.innerHTML=`<div class="detail-hero"><div class="eyebrow">${escapeHtml(item.type||"ATTRACTION")} · ${escapeHtml(item.city||"INDIA")}</div><h2>${escapeHtml(item.name)}</h2><p class="detail-description">${escapeHtml(item.significance||"A destination worth discovering in India.")}. Use the details below to decide whether it fits your next trip.</p></div>
 <div class="detail-metrics"><div class="detail-metric"><strong>★ ${Number(item.rating||0).toFixed(1)}</strong><span>Google rating</span></div><div class="detail-metric"><strong>${money(item.entrance_fee)}</strong><span>Entrance fee</span></div><div class="detail-metric"><strong>${Number(item.visit_hours||0)} hrs</strong><span>Visit duration</span></div></div>
 <div class="detail-facts"><div><span>STATE</span><b>${escapeHtml(item.state||"Not listed")}</b></div><div><span>BEST TIME TO VISIT</span><b>${escapeHtml(item.best_time||"Not specified")}</b></div><div><span>AIRPORT WITHIN 50 KM</span><b>${escapeHtml(item.airport_nearby||"Not specified")}</b></div><div><span>DSLR ALLOWED</span><b>${escapeHtml(item.dslr_allowed||"Not specified")}</b></div><div><span>WEEKLY OFF</span><b>${escapeHtml(item.weekly_off||"Not specified")}</b></div><div><span>REVIEWS (LAKHS)</span><b>${Number(item.review_lakhs||0).toFixed(2)}</b></div></div>
 <div style="margin-top:22px;display:flex;gap:10px;flex-wrap:wrap"><button class="button button-dark" data-favorite="${item.id}">♡ Save this place</button><a class="button button-outline" href="/planner">Plan a trip ↗</a></div>`;
 modal.hidden=false;
}
$("#closeModal")?.addEventListener("click",()=>$("#detailModal").hidden=true);
$("#detailModal")?.addEventListener("click",e=>{if(e.target.id==="detailModal")e.currentTarget.hidden=true});
document.addEventListener("keydown",e=>{if(e.key==="Escape"&&$("#detailModal"))$("#detailModal").hidden=true});
