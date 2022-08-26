/*! For license information please see 167-bundle.js.LICENSE.txt */
"use strict";(self.webpackChunkorganilab=self.webpackChunkorganilab||[]).push([[167],{167:(e,t,n)=>{n.r(t),n.d(t,{default:()=>i});const o=async function(e){let t;const n=e.configObj.pref("lang");try{t=await function(e){switch(e){case"./locale/en.js":return Promise.resolve().then((function(){return r}));case"./locale/fr.js":return Promise.resolve().then((function(){return a}));case"./locale/tr.js":return Promise.resolve().then((function(){return s}));case"./locale/zh-CN.js":return Promise.resolve().then((function(){return c}));default:return new Promise((function(t,n){("function"==typeof queueMicrotask?queueMicrotask:setTimeout)(n.bind(null,new Error("Unknown variable dynamic import: "+e)))}))}}("./locale/".concat(n,".js"))}catch(e){console.warn("Missing translation (".concat(n,") for ").concat("grid"," - using 'en'")),t=await Promise.resolve().then((function(){return r}))}e.i18next.addResourceBundle(n,"grid",t.default)};var i={name:"grid",async init(){const e=this;await o(e);const{svgCanvas:t}=e,{$id:n,$click:i,NS:r}=t,a=n("svgcanvas").ownerDocument,{assignAttributes:s}=t,c=document.createElement("canvas"),l=n("canvasBackground"),d=t.getTypeMap(),u=[.01,.1,1,10,100,1e3];let g=e.configObj.curConfig.showGrid||!1;c.style.display="none",e.$svgEditor.appendChild(c);const h=a.createElementNS(r.SVG,"svg");s(h,{id:"canvasGrid",width:"100%",height:"100%",x:0,y:0,overflow:"visible",display:"none"}),l.appendChild(h);const p=a.createElementNS(r.SVG,"defs"),f=a.createElementNS(r.SVG,"pattern");s(f,{id:"gridpattern",patternUnits:"userSpaceOnUse",x:0,y:0,width:100,height:100});const m=a.createElementNS(r.SVG,"image");s(m,{x:0,y:0,width:100,height:100}),f.append(m),p.append(f),n("canvasGrid").appendChild(p);const b=a.createElementNS(r.SVG,"rect");s(b,{width:"100%",height:"100%",x:0,y:0,"stroke-width":0,stroke:"none",fill:"url(#gridpattern)",style:"pointer-events: none; display:visible;"}),n("canvasGrid").appendChild(b);const v=n=>{const o=d[e.configObj.curConfig.baseUnit]*n,i=100/o;let r=1;u.some((e=>(r=e,i<=e)));const a=r*o;c.width=a,c.height=a;const s=c.getContext("2d"),l=.5,g=a/10;s.globalAlpha=.2,s.strokeStyle=e.configObj.curConfig.gridColor;for(let e=1;e<10;e++){const t=Math.round(g*e)+.5,n=0;s.moveTo(t,a),s.lineTo(t,n),s.moveTo(a,t),s.lineTo(n,t)}s.stroke(),s.beginPath(),s.globalAlpha=.5,s.moveTo(l,a),s.lineTo(l,0),s.moveTo(a,l),s.lineTo(0,l),s.stroke();const h=c.toDataURL("image/png");m.setAttribute("width",a),m.setAttribute("height",a),m.parentNode.setAttribute("width",a),m.parentNode.setAttribute("height",a),t.setHref(m,h)},w=()=>{g&&v(t.getZoom()),n("canvasGrid").style.display=g?"block":"none",n("view_grid").pressed=g};return{name:e.i18next.t("".concat("grid",":name")),zoomChanged(e){g&&v(e)},callback(){const t=document.createElement("template"),o="".concat("grid",":buttons.0.title");t.innerHTML='\n          <se-button id="view_grid" title="'.concat(o,'" src="grid.svg"></se-button>\n        '),n("editor_panel").append(t.content.cloneNode(!0)),i(n("view_grid"),(()=>{e.configObj.curConfig.showGrid=g=!g,w()})),g&&w()}}}},r=Object.freeze({__proto__:null,default:{name:"View Grid",buttons:[{title:"Show/Hide Grid"}]}}),a=Object.freeze({__proto__:null,default:{name:"Grille",buttons:[{title:"Afficher/Cacher Grille"}]}}),s=Object.freeze({__proto__:null,default:{name:"Izgarayı Görüntüle",buttons:[{title:"Izgara Göster/Gizle"}]}}),c=Object.freeze({__proto__:null,default:{name:"网格视图",buttons:[{title:"显示/隐藏网格"}]}})}}]);