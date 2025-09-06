// ======= CONFIGURE AQUI =======
const firebaseConfig = {
  apiKey: "SUA_API_KEY",
  authDomain: "SEU_PROJETO.firebaseapp.com",
  projectId: "SEU_PROJETO",
  appId: "SUA_APP_ID",
};
// ==============================

(function(){
  // carrega SDKs sem travar a página
  const s = document.createElement('script');
  s.src = "https://www.gstatic.com/firebasejs/10.12.4/firebase-app-compat.js";
  s.onload = ()=>{
    const a=document.createElement('script');
    a.src="https://www.gstatic.com/firebasejs/10.12.4/firebase-auth-compat.js";
    a.onload = initAuth;
    document.head.appendChild(a);
  };
  document.head.appendChild(s);
})();

function initAuth(){
  firebase.initializeApp(firebaseConfig);
  const auth = firebase.auth();
  const google = new firebase.auth.GoogleAuthProvider();
  const microsoft = new firebase.auth.OAuthProvider('microsoft.com');

  const loginBtn = document.getElementById('loginBtn');
  const logoutBtn = document.getElementById('logoutBtn');

  function updateUI(user){
    if(user){
      window._uid = user.uid;
      loginBtn.style.display='none';
      logoutBtn.style.display='inline-block';
      document.dispatchEvent(new Event('auth-ready'));
    }else{
      window._uid = '';
      loginBtn.style.display='inline-block';
      logoutBtn.style.display='none';
    }
  }

  if(loginBtn){
    loginBtn.onclick = async ()=>{
      try {
        // primeiro tenta Google, se cancelar abre Microsoft
        await auth.signInWithPopup(google).catch(async ()=>{
          await auth.signInWithPopup(microsoft);
        });
      }catch(e){ alert('Falha no login'); console.error(e); }
    };
  }
  if(logoutBtn){ logoutBtn.onclick = ()=>auth.signOut(); }

  auth.onAuthStateChanged(updateUI);
}
