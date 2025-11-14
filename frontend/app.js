const API = location.origin.replace(/:\d+$/,":8000")
const state = { cats: [], currentCat: null, userId: 1001 }

function $(sel){ return document.querySelector(sel) }
function el(tag, attrs={}, children=[]) { const e=document.createElement(tag); Object.entries(attrs).forEach(([k,v])=>e[k]=v); children.forEach(c=>e.append(c)); return e }
function icon(name){ const s=document.createElement("span"); s.innerHTML=name; s.style.marginRight="4px"; return s }
function prettyDate(ts){ const d=new Date(ts); return d.toLocaleString("zh-CN", { month:"numeric", day:"numeric", hour:"2-digit", minute:"2-digit" }) }

async function fetchJSON(url, opts={}){
  const res = await fetch(url, { ...opts, headers: { ...(opts.headers||{}), 'X-User-Id': state.userId } })
  if(!res.ok) throw new Error(await res.text())
  return res.json()
}

async function loadCats(){
  state.cats = await fetchJSON(`${API}/api/cats`)
}

function renderCats(){
  const v = $("#view"); v.innerHTML = ""
  const grid = el("div", { className:"grid" })
  state.cats.forEach(c=>{
    const card = el("div", { className:"card" }, [
      el("img", { src: c.profile_image_url || "https://dummyimage.com/600x400/ffd8d9/000&text=🐱" }),
      el("div", { className:"content" }, [
        el("div", { className:"name" }, [c.name]),
        el("div", { className:"toolbar" }, [
          el("button", { className:"btn", onclick:()=>{ state.currentCat=c; switchTab('report') } }, [icon("📍"),"上报"]),
          el("button", { className:"btn", onclick:()=>{ state.currentCat=c; switchTab('feed') } }, [icon("🍱"),"喂食"]),
          el("button", { className:"btn", onclick:()=>{ state.currentCat=c; switchTab('timeline') } }, [icon("📖"),"时间轴"]),
        ])
      ])
    ])
    grid.append(card)
  })
  v.append(grid)
}

function renderReport(){
  const c = state.currentCat || state.cats[0]
  const v = $("#view"); v.innerHTML = ""
  v.append(el("div", {}, [
    el("div", { className:"input" }, [ el("label", {}, [icon("🐱"),"选择猫咪"]), selectCat() ]),
    el("div", { className:"input" }, [ el("label", {}, [icon("📍"),"地点"]), el("input", { id:"loc", placeholder:"例如：9号楼" }) ]),
    el("div", { className:"input" }, [ el("label", {}, [icon("📸"),"照片"]), el("input", { id:"photo", type:"file", accept:"image/*" }) ]),
    el("button", { className:"btn", onclick: submitSighting }, [icon("✨"),"提交上报"])
  ]))
}

function selectCat(){
  const sel = el("select", { id:"catSel" })
  state.cats.forEach(c=>{ const o=document.createElement("option"); o.value=c.cat_id; o.textContent=c.name; sel.append(o) })
  if(state.currentCat) sel.value = state.currentCat.cat_id
  return sel
}

async function submitSighting(){
  const catId = parseInt($("#catSel").value,10)
  const loc = $("#loc").value
  const file = $("#photo").files[0]
  const fd = new FormData(); fd.append("cat_id", catId); fd.append("location", loc); if(file) fd.append("photo", file)
  const res = await fetch(`${API}/api/sightings`, { method:"POST", body: fd, headers: { 'X-User-Id': state.userId } })
  if(!res.ok){ alert(await res.text()); return }
  alert("上报成功")
  switchTab('timeline')
}

function renderFeed(){
  const v = $("#view"); v.innerHTML = ""
  v.append(el("div", {}, [
    el("div", { className:"input" }, [ el("label", {}, [icon("🐱"),"选择猫咪"]), selectCat() ]),
    el("div", { className:"input" }, [ el("label", {}, [icon("🍱"),"食物类型"]), el("input", { id:"food", placeholder:"猫粮/罐头" }) ]),
    el("div", { className:"input" }, [ el("label", {}, [icon("⚖️"),"数量"]), el("input", { id:"amt", placeholder:"例如：50g" }) ]),
    el("button", { className:"btn", onclick: submitFeeding }, [icon("🥰"),"提交喂食"])
  ]))
}

async function submitFeeding(){
  const catId = parseInt($("#catSel").value,10)
  const food = $("#food").value
  const amt = $("#amt").value
  await fetchJSON(`${API}/api/feedings`, { method:"POST", headers:{ 'Content-Type':'application/json' }, body: JSON.stringify({ cat_id: catId, food_type: food, amount: amt }) })
  alert("喂食记录成功")
  switchTab('timeline')
}

async function renderTimeline(){
  const c = state.currentCat || state.cats[0]; if(!c){ await loadCats(); }
  const catId = (state.currentCat||state.cats[0]).cat_id
  const v = $("#view"); v.innerHTML = ""
  const items = await fetchJSON(`${API}/api/cats/${catId}/timeline`)
  const list = el("div", { className:"timeline" })
  items.forEach(it=>{
    const isSighting = it.type === "sighting"
    const d = el("div", { className:"item" }, [
      el("div", { className:"meta" }, [ (isSighting ? "📍 轨迹" : "🍱 喂食") + " · " + prettyDate(it.timestamp) ]),
      el("div", {}, [ isSighting ? `地点：${it.data.location}` : `食物：${it.data.food_type} · ${it.data.amount}` ])
    ])
    list.append(d)
  })
  v.append(list)
}

async function renderCommunity(){
  const v = $("#view"); v.innerHTML = ""
  const input = el("textarea", { id:"postText", rows:4, placeholder:"分享一件校园猫咪趣事" })
  const gen = el("button", { className:"btn", onclick: async ()=>{
    const t = input.value
    const r = await fetchJSON(`${API}/api/ai/generate-cat-speech`, { method:"POST", body: new URLSearchParams({ user_text: t }) })
    input.value = `${t}\n${r.text}`
  } }, [icon("✨"),"AI 生成猫言猫语"])
  const img = el("input", { id:"postImg", type:"file", accept:"image/*" })
  const send = el("button", { className:"btn", onclick: async ()=>{
    const fd = new FormData(); fd.append("user_id", state.userId); fd.append("content_text", input.value); const f=img.files[0]; if(f) fd.append("content_image", f)
    const res = await fetch(`${API}/api/community/posts`, { method:"POST", body: fd })
    if(!res.ok){ alert(await res.text()); return }
    alert("发布成功"); renderCommunity()
  } }, [icon("🚀"),"发布"])
  v.append(el("div", { className:"list" }, [ input, el("div", { className:"toolbar" }, [gen, img, send]) ]))
  const feed = await fetchJSON(`${API}/api/community/posts`)
  const grid = el("div", { className:"list" })
  feed.items.forEach(p=>{
    const card = el("div", { className:"item" }, [
      el("div", { className:"meta" }, [ `🐱 #${p.post_id} · ${prettyDate(p.timestamp)}` ]),
      el("div", {}, [ p.content_text ]),
      p.content_image_url ? el("img", { src: p.content_image_url, style:"width:100%;border-radius:8px;margin-top:8px" }) : ""
    ])
    grid.append(card)
  })
  v.append(grid)
}

async function renderMe(){
  const v = $("#view"); v.innerHTML = ""
  const prof = await fetchJSON(`${API}/api/users/${state.userId}/profile`)
  const badges = await fetchJSON(`${API}/api/users/${state.userId}/badges`)
  const head = el("div", { className:"row" }, [
    el("img", { src: prof.avatar_url || "https://dummyimage.com/80x80/ffd8d9/000&text=😺", style:"width:80px;height:80px;border-radius:50%;box-shadow:var(--shadow)" }),
    el("div", {}, [ el("div", { style:"font-size:18px;font-weight:600" }, [ prof.nickname || "校园爱猫人" ]) ])
  ])
  const wall = el("div", { className:"badge-grid" })
  badges.forEach(b=>{
    wall.append(el("div", { className:"badge-card" }, [
      el("img", { src: b.icon_url || "https://dummyimage.com/300x200/ffd8d9/000&text=🏅" }),
      el("div", { className:"name" }, [ b.name ])
    ]))
  })
  v.append(el("div", { className:"list" }, [ head, wall ]))
}

async function switchTab(tab){
  document.querySelectorAll('.tabbar button').forEach(b=>b.classList.remove('active'))
  document.querySelector(`.tabbar button[data-tab="${tab}"]`).classList.add('active')
  if(tab==='cats'){ await loadCats(); renderCats() }
  else if(tab==='report'){ await loadCats(); renderReport() }
  else if(tab==='feed'){ await loadCats(); renderFeed() }
  else if(tab==='timeline'){ await loadCats(); await renderTimeline() }
  else if(tab==='community'){ await renderCommunity() }
  else if(tab==='me'){ await renderMe() }
}

window.addEventListener('load', async ()=>{
  await loadCats()
  switchTab('cats')
  document.querySelectorAll('.tabbar button').forEach(b=>b.addEventListener('click', ()=>switchTab(b.dataset.tab)))
})