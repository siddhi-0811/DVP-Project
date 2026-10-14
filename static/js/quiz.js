let questions=[],index=0,score=0,answered=false;
$("#startQuiz").addEventListener("click",startQuiz);
async function startQuiz(){try{questions=await api("/api/quiz/questions");index=0;score=0;renderQuestion()}catch(e){toast(e.message)}}
function renderQuestion(){
 answered=false;const q=questions[index];
 $("#quizMain").innerHTML=`<div class="quiz-progress"><span>QUESTION ${index+1} OF ${questions.length}</span><b>${score} POINTS</b></div><div class="progress-track"><div class="progress-fill" style="width:${(index/questions.length)*100}%"></div></div><span class="mini-label">DESTINATION DETECTIVE</span><h2 class="quiz-question">${escapeHtml(q.question)}</h2><p class="quiz-hint">Hint: ${escapeHtml(q.hint)}</p><div class="quiz-options">${q.options.map((o,i)=>`<button class="quiz-option" data-answer="${escapeHtml(o)}">${String.fromCharCode(65+i)}. &nbsp;${escapeHtml(o)}</button>`).join("")}</div><div id="quizFeedback"></div><div class="quiz-controls"><span class="card-location">10 points for a correct answer</span><button class="button button-dark" id="nextQuestion" disabled>${index===questions.length-1?"See results":"Next question"} ↗</button></div>`;
 $$(".quiz-option").forEach(btn=>btn.addEventListener("click",()=>answerQuestion(btn,q)));
 $("#nextQuestion").addEventListener("click",()=>{if(!answered)return;if(index<questions.length-1){index++;renderQuestion()}else showResults()});
}
function answerQuestion(btn,q){
 if(answered)return;answered=true;
 const correct=btn.dataset.answer===q.answer;if(correct)score+=10;
 $$(".quiz-option").forEach(option=>{option.disabled=true;if(option.dataset.answer===q.answer)option.classList.add("correct")});
 if(!correct)btn.classList.add("wrong");
 $("#quizFeedback").innerHTML=`<div class="quiz-feedback"><b>${correct?"That's right! +10 points":"Not quite — the answer is "+escapeHtml(q.answer)+"."}</b><br>${escapeHtml(q.fact)}</div>`;
 $("#nextQuestion").disabled=false;
}
async function showResults(){
 const total=questions.length*10;
 try{await api("/api/quiz/submit",{method:"POST",body:JSON.stringify({score,total:questions.length*10})})}catch(e){}
 const percent=Math.round(score/total*100);
 const title=percent>=80?"India Explorer Extraordinaire":percent>=50?"Curious Traveller":"Adventure Beginner";
 $("#quizMain").innerHTML=`<div class="quiz-result"><div class="quiz-big-icon">✦</div><span class="mini-label">YOUR EXPLORER SCORE</span><div class="quiz-result-score">${score}<span style="font-size:20px;color:#92a39a">/${total}</span></div><h2>${title}</h2><p class="detail-description">You got ${score/10} out of ${questions.length} questions right. Every trip is a chance to learn something new.</p><button id="playAgain" class="button button-dark">Play again ↻</button> <a href="/destinations" class="button button-outline">Explore places ↗</a></div>`;
 $("#playAgain").addEventListener("click",startQuiz);
}
