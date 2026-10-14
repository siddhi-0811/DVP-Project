let allResults=[], shown=0, savedIds=new Set();
const PAGE_SIZE=12;
async function loadFilters(){
 const data=await api("/api/filters");
 data.states.forEach(s=>$("#stateFilter").insertAdjacentHTML("beforeend",`<option value="${escapeHtml(s)}">${escapeHtml(s)}</option>`));
 data.types.forEach(t=>$("#typeFilter").insertAdjacentHTML("beforeend",`<option value="${escapeHtml(t)}">${escapeHtml(t)}</option>`));
}
function params(){return new URLSearchParams({q:$("#searchInput").value,state:$("#stateFilter").value,type:$("#typeFilter").value,min_rating:$("#ratingFilter").value,max_fee:$("#feeFilter").value,sort:$("#sortFilter").value})}
async function loadDestinations(reset=true){
 if(reset){shown=0;$("#destinationGrid").innerHTML='<div class="loading-card">Finding your next adventure…</div>'}
 try{
  allResults=await api("/api/destinations?"+params());
  const favs=await api("/api/favorites");savedIds=new Set(favs.map(x=>Number(x.id)));
  renderResults();
  $("#exportCsv").href="/api/export/destinations.csv?"+params();
 }catch(e){$("#destinationGrid").innerHTML=`<div class="loading-card">${escapeHtml(e.message)}</div>`}
}
function renderResults(){
 const results=allResults.slice(0,shown+PAGE_SIZE);
 shown=results.length;
 $("#resultsCount").innerHTML=`Showing <strong>${allResults.length?1:0}–${shown}</strong> of <strong>${allResults.length}</strong> destinations`;
 $("#destinationGrid").innerHTML=results.map(x=>cardHtml(x,{savedIds})).join("")||'<div class="empty-state"><span>⌕</span><h3>No places found</h3><p>Try another search or reset some filters.</p></div>';
 $("#loadMore").hidden=shown>=allResults.length;
}
let searchTimer;
$("#searchInput").addEventListener("input",()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>loadDestinations(),220)});
["stateFilter","typeFilter","ratingFilter","feeFilter","sortFilter"].forEach(id=>$("#"+id).addEventListener("change",()=>loadDestinations()));
$("#resetFilters").addEventListener("click",()=>{$("#searchInput").value="";["stateFilter","typeFilter","ratingFilter","feeFilter"].forEach(id=>$("#"+id).value="");$("#sortFilter").value="rating";loadDestinations()});
$("#loadMore").addEventListener("click",renderResults);
const searchValue=new URLSearchParams(location.search).get("q");if(searchValue)$("#searchInput").value=searchValue;
loadFilters().then(loadDestinations);
