let spamChart = null;

async function checkAuth() {
    try {
        const res = await fetch(`${BASE_URL}/api/check-auth`);
        const data = await res.json();
        renderUI(data.authenticated);
    } catch(e){console.error(e);}
}

function renderUI(authenticated){
    const nav=document.getElementById('nav');
    const main=document.getElementById('main');
    if(!authenticated){
        nav.innerHTML='';
        main.innerHTML=`
        <div id="loginSection">
            <h2>Login / Register</h2>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:30px;">
            <div>
                <h3>Login</h3>
                <form id="loginForm">
                    <div class="form-group"><label>Email</label><input type="email" id="loginEmail" required></div>
                    <div class="form-group"><label>Password</label><input type="password" id="loginPassword" required></div>
                    <button type="submit" class="btn">Login</button>
                </form>
            </div>
            <div>
                <h3>Register</h3>
                <form id="registerForm">
                    <div class="form-group"><label>Email</label><input type="email" id="regEmail" required></div>
                    <div class="form-group"><label>Password</label><input type="password" id="regPassword" required></div>
                    <button type="submit" class="btn">Register</button>
                </form>
            </div>
            </div>
            <div id="message" style="margin-top:20px;padding:15px;border-radius:5px;display:none;"></div>
        </div>`;
        document.getElementById('loginForm').addEventListener('submit', handleLogin);
        document.getElementById('registerForm').addEventListener('submit', handleRegister);
    } else {
        nav.innerHTML=`<button class="btn" onclick="logout()">Logout</button>`;
        main.innerHTML=`
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
            <div id="detectorSection">
                <h2>Check Message</h2>
                <form id="spamForm">
                    <div class="form-group">
                        <label for="message">Enter message:</label>
                        <textarea id="message" placeholder="Paste message here..." required></textarea>
                    </div>
                    <button type="submit" class="btn" style="width:100%;">Detect Spam</button>
                </form>
                <div id="result"></div>
            </div>
            <div id="statsSection">
                <h2>Your Statistics</h2>
                <div id="stats"></div>
                <canvas id="spamChart" style="margin-top:20px;"></canvas>
            </div>
        </div>
        <div id="historySection" style="margin-top:30px;">
            <h2>Recent Predictions</h2>
            <div id="history"></div>
        </div>`;
        document.getElementById('spamForm').addEventListener('submit', handleSpamDetection);
        loadStats();
        loadHistory();
    }
}

async function handleLogin(e){
    e.preventDefault();
    const email=document.getElementById('loginEmail').value;
    const password=document.getElementById('loginPassword').value;
    try{
        const res=await fetch(`${BASE_URL}/api/login`, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password})});
        const data=await res.json();
        if(res.ok){showMessage('Login successful','success');setTimeout(()=>checkAuth(),1000);}
        else{showMessage(data.error||'Login failed','error');}
    } catch(e){showMessage('Error: '+e.message,'error');}
}

async function handleRegister(e){
    e.preventDefault();
    const email=document.getElementById('regEmail').value;
    const password=document.getElementById('regPassword').value;
    try{
        const res=await fetch(`${BASE_URL}/api/register`, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password})});
        const data=await res.json();
        if(res.ok){showMessage('Registration successful! Please login.','success');}
        else{showMessage(data.error||'Registration failed','error');}
    }catch(e){showMessage('Error: '+e.message,'error');}
}

async function handleSpamDetection(e){
    e.preventDefault();
    const message=document.getElementById('message').value;
    try{
        const res=await fetch(`${BASE_URL}/api/detect-spam`, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message})});
        const data=await res.json();
        if(res.ok){
            const resultDiv=document.getElementById('result');
            const spamConf=(data.spam_confidence*100).toFixed(2);
            const hamConf=(data.ham_confidence*100).toFixed(2);
            resultDiv.innerHTML=`
                <div class="prediction-card">
                    <div class="prediction-label">${data.prediction}</div>
                    <div class="confidence">
                        <div class="confidence-bar"><label>SPAM: ${spamConf}%</label><div class="bar"><div class="bar-fill" style="width:${spamConf}%"></div></div></div>                        <div class="confidence-bar"><label>HAM: ${hamConf}%</label><div class="bar"><div class="bar-fill" style="width:${hamConf}%"></div></div></div>
                    </div>
                </div>
            `;
            loadStats();
            loadHistory();
        } else {
            showMessage(data.error || 'Detection failed','error');
        }
    } catch(e){
        showMessage('Error: ' + e.message,'error');
    }
}

async function loadStats(){
    try{
        const res=await fetch(`${BASE_URL}/api/stats`);
        const data=await res.json();
        if(res.ok){
            const statsDiv=document.getElementById('stats');
            statsDiv.innerHTML=`
                <div style="background:#f5f5f5;padding:15px;border-radius:5px;">
                    <p><strong>Total Messages:</strong> ${data.total_messages}</p>
                    <p><strong>Spam:</strong> ${data.spam_count} (${data.spam_percentage.toFixed(1)}%)</p>
                    <p><strong>Ham:</strong> ${data.ham_count}</p>
                    <p><strong>Avg Spam Confidence:</strong> ${(data.avg_spam_confidence*100).toFixed(2)}%</p>
                    <p><strong>Avg Message Length:</strong> ${data.avg_message_length.toFixed(0)} chars</p>
                </div>
            `;
            // Draw chart
            const ctx=document.getElementById('spamChart').getContext('2d');
            if(spamChart) spamChart.destroy();
            spamChart=new Chart(ctx,{
                type:'doughnut',
                data:{
                    labels:['Spam','Ham'],
                    datasets:[{
                        data:[data.spam_count,data.ham_count],
                        backgroundColor:['#ff6b6b','#4ecdc4']
                    }]
                }
            });
        }
    } catch(e){console.error('Failed to load stats:',e);}
}

async function loadHistory(){
    try{
        const res=await fetch(`${BASE_URL}/api/history?limit=5`);
        const predictions=await res.json();
        if(res.ok && predictions.length>0){
            const historyDiv=document.getElementById('history');
            historyDiv.innerHTML=predictions.map(p=>`
                <div style="background:#f5f5f5;padding:15px;margin-bottom:10px;border-radius:5px;border-left:4px solid ${p.prediction==='SPAM'?'#ff6b6b':'#4ecdc4'};">
                    <p><strong>${p.prediction}</strong> - ${(p.spam_confidence*100).toFixed(2)}% confidence</p>
                    <p style="color:#666;font-size:12px;">"${p.message.substring(0,50)}..."</p>
                    <p style="color:#999;font-size:12px;">${new Date(p.timestamp).toLocaleString()}</p>
                </div>
            `).join('');
        }
    } catch(e){console.error('Failed to load history:',e);}
}

async function logout(){
    try{
        await fetch(`${BASE_URL}/api/logout`, {method:'POST'});
        checkAuth();
    } catch(e){console.error('Logout failed:',e);}
}

function showMessage(text,type){
    const messageDiv=document.getElementById('message');
    if(messageDiv){
        messageDiv.textContent=text;
        messageDiv.style.background=type==='success'?'#d4edda':'#f8d7da';
        messageDiv.style.color=type==='success'?'#155724':'#721c24';
        messageDiv.style.display='block';
        setTimeout(()=>{messageDiv.style.display='none';},3000);
    }
}