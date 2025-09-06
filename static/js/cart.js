const PRICES = {
  pendrive_android: 35.00,
  pendrive_linux: 40.00
};
const NAMES = {
  pendrive_android: "Pendrive Boot Android/Google TV",
  pendrive_linux: "Pendrive Boot Linux"
};

function getCart(){
  try{ return JSON.parse(localStorage.getItem('fluxy_cart')||'[]'); }catch(e){ return []; }
}
function saveCart(arr){
  localStorage.setItem('fluxy_cart', JSON.stringify(arr));
  updateCartCount();
}
function addToCart(key){
  const cart = getCart();
  const idx = cart.findIndex(x=>x.key===key);
  if(idx>=0) cart[idx].qty += 1; else cart.push({key, qty:1});
  saveCart(cart);
  alert('Adicionado ao carrinho!');
}
function removeFromCart(key){
  let cart = getCart().filter(x=>x.key!==key);
  saveCart(cart);
  renderCartList('cart-list'); renderCartSummary('cart-summary');
}
function updateQty(key, qty){
  qty = Math.max(1, parseInt(qty||1));
  const cart = getCart();
  const it = cart.find(x=>x.key===key); if(it){ it.qty=qty; }
  saveCart(cart);
  renderCartList('cart-list'); renderCartSummary('cart-summary');
}
function cartTotals(){
  const cart = getCart();
  let total = 0;
  cart.forEach(i=> total += (PRICES[i.key]||0)*i.qty);
  return {cart, total};
}
function money(n){ return n.toFixed(2).replace('.',','); }

function renderCartList(elid){
  const el = document.getElementById(elid); if(!el) return;
  const {cart,total} = cartTotals();
  if(!cart.length){ el.innerHTML = "<p>Seu carrinho está vazio.</p>"; return; }
  el.innerHTML = cart.map(i=>`
    <div class="row">
      <b>${NAMES[i.key]}</b>
      <div>R$ ${money(PRICES[i.key])}</div>
      <div>
        <input type="number" min="1" value="${i.qty}" onchange="updateQty('${i.key}', this.value)" style="width:80px">
        <button class="btn outline" onclick="removeFromCart('${i.key}')">Remover</button>
      </div>
    </div>
  `).join('') + `<p class="price">Total: R$ ${money(total)}</p>`;
}
function renderCartSummary(elid){
  const el = document.getElementById(elid); if(!el) return;
  const {cart,total} = cartTotals();
  if(!cart.length){ el.innerHTML = "<p>Seu carrinho está vazio.</p>"; return; }
  el.innerHTML = `
    <ul>${cart.map(i=>`<li>${NAMES[i.key]} — ${i.qty}x (R$ ${money(PRICES[i.key])})</li>`).join('')}</ul>
    <p class="price">Total: R$ ${money(total)}</p>
  `;
}
function updateCartCount(){
  const c = getCart(); const n = c.reduce((s,i)=>s+i.qty,0);
  const el = document.getElementById('cart-count'); if(el) el.textContent = n;
}
document.addEventListener('DOMContentLoaded', updateCartCount);
if(typeof window!=='undefined'){ window.getCart=getCart; window.renderCartList=renderCartList; window.renderCartSummary=renderCartSummary; }
