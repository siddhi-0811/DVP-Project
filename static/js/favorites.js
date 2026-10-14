async function loadFavorites(){
 try{
  const items=await api("/api/favorites");
  $("#favoritesCount").innerHTML=`<strong>${items.length}</strong> ${items.length===1?"place":"places"} in your collection`;
  $("#favoritesGrid").innerHTML=items.map(x=>cardHtml(x,{savedIds:new Set(items.map(i=>Number(i.id)))})).join("");
  $("#emptyFavorites").hidden=items.length>0;
  $("#favoritesGrid").hidden=items.length===0;
 }catch(e){$("#favoritesGrid").innerHTML=`<div class="loading-card">${escapeHtml(e.message)}</div>`}
}
document.addEventListener("favoritesChanged",loadFavorites);
document.addEventListener("click",e=>{if(e.target.closest("[data-favorite]"))setTimeout(loadFavorites,200)});
loadFavorites();
