let currentPlan=null;
async function setupPlanner(){
 const filters=await api("/api/filters");
 filters.states.forEach(s=>$("#plannerState").insertAdjacentHTML("beforeend",`<option value="${escapeHtml(s)}">${escapeHtml(s)}</option>`));
 filters.types.forEach(t=>$("#plannerType").insertAdjacentHTML("beforeend",`<option value="${escapeHtml(t)}">${escapeHtml(t)}</option>`));
}
function updateSliders(){$("#budgetValue").textContent="₹"+Number($("#budgetRange").value).toLocaleString("en-IN");$("#hoursValue").textContent=$("#hoursRange").value+" hours"}
$("#budgetRange").addEventListener("input",updateSliders);$("#hoursRange").addEventListener("input",updateSliders);updateSliders();setupPlanner();
$("#plannerForm").addEventListener("submit",async e=>{
 e.preventDefault();const data=Object.fromEntries(new FormData(e.currentTarget).entries());data.budget=Number(data.budget);data.hours=Number(data.hours);data.rating=Number(data.rating);data.count=Number(data.count);
 const btn=e.submitter;btn.disabled=true;btn.textContent="Building your trip…";
 try{
  const result=await api("/api/plan",{method:"POST",body:JSON.stringify(data)});currentPlan=result;
  // Keep the exportable plan in the same browser session.
  sessionStorage.setItem("latestPlan",JSON.stringify(result));
  $("#planResultsSection").hidden=false;
  $("#planMessage").textContent=result.items.length?result.message:"No destinations match every limit. Try a higher budget, more time, or a lower rating.";
  $("#planMetrics").innerHTML=`<div class="plan-metric"><span>Entrance fee total</span><strong>₹${result.total_fee.toLocaleString("en-IN")}</strong></div><div class="plan-metric"><span>Visit time planned</span><strong>${result.total_hours} h</strong></div><div class="plan-metric"><span>Budget remaining</span><strong>₹${result.remaining_budget.toLocaleString("en-IN")}</strong></div><div class="plan-metric"><span>Places selected</span><strong>${result.items.length}</strong></div>`;
  $("#planItems").innerHTML=result.items.map((item,i)=>`<article class="plan-item"><span class="plan-item-num">${String(i+1).padStart(2,"0")}</span><div><h3>${escapeHtml(item.name)}</h3><p>${escapeHtml([item.city,item.state,item.type].filter(Boolean).join(" · "))}<br>★ ${item.rating.toFixed(1)} · ${item.visit_hours} hours · Best time: ${escapeHtml(item.best_time)}</p></div><span class="plan-fee">${money(item.entrance_fee)}</span></article>`).join("")||'<div class="empty-state">No matches. Adjust your preferences and try again.</div>';
  $("#downloadPlan").disabled=!result.items.length;$("#downloadPlan").dataset.id=result.plan_id;
  $("#planResultsSection").scrollIntoView({behavior:"smooth",block:"start"});toast("Your itinerary is ready!");
 }catch(err){toast(err.message)}finally{btn.disabled=false;btn.innerHTML='Build my itinerary <span>↗</span>'}
});
$("#downloadPlan").addEventListener("click",()=>{
 if(!currentPlan)return;
 window.location.href=`/api/export/plan/${currentPlan.plan_id}.pdf`;
});
