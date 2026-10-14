document.addEventListener("DOMContentLoaded",async()=>{
 try{
  const stats=await api("/api/dashboard");
  $("#statPlaces").textContent=stats.total.toLocaleString();
  $("#statStates").textContent=stats.states;
  $("#statRating").textContent=stats.avg_rating.toFixed(1)+"/5";
  $("#statFee").textContent="₹"+Math.round(stats.avg_fee).toLocaleString("en-IN");
  const top=stats.top_destinations.slice(0,3);
  const favs=await api("/api/favorites");const ids=new Set(favs.map(x=>Number(x.id)));
  $("#featuredGrid").innerHTML=top.map(x=>cardHtml(x,{savedIds:ids})).join("");
 }catch(e){$("#featuredGrid").innerHTML='<div class="loading-card">Could not load attractions. Check that the app is running and the database is ready.</div>'}
 $$(".category-chip").forEach(btn=>btn.addEventListener("click",async()=>{
  $$(".category-chip").forEach(b=>b.classList.remove("active"));btn.classList.add("active");
  const type=btn.dataset.type;
  const items=await api("/api/destinations?"+new URLSearchParams({type,sort:"rating"}));
  const favs=await api("/api/favorites");const ids=new Set(favs.map(x=>Number(x.id)));
  $("#featuredGrid").innerHTML=items.slice(0,3).map(x=>cardHtml(x,{savedIds:ids})).join("")||'<div class="loading-card">No attractions in this category yet.</div>';
 }));
});
