import React, {useEffect, useState} from 'react';
import {createRoot} from 'react-dom/client';
import Plotly from 'plotly.js-dist-min';
import './style.css';

const API = import.meta.env.VITE_API_URL || '';
const airports = ['DEL','BOM','BLR','MAA','HYD','CCU'];
const money = n => `₹${Number(n).toLocaleString('en-IN')}`;

function Chart({data, type='scatter', x, y, names}) {
  useEffect(() => { if (!data?.length) return; Plotly.newPlot('flight-chart', data.map((series, i) => ({x: series[x], y: series[y], type, mode: type==='scatter'?'lines+markers':undefined, name: names?.[i] || series.name || ''})), {paper_bgcolor:'transparent', plot_bgcolor:'transparent', font:{color:'#9fb0c1'}, margin:{l:45,r:15,t:12,b:38}, legend:{orientation:'h'}, xaxis:{gridcolor:'#243446'}, yaxis:{gridcolor:'#243446', tickprefix:'₹'}}, {responsive:true, displayModeBar:false}); return () => Plotly.purge('flight-chart'); }, [data, type, x, y, names]);
  return <div id="flight-chart" className="chart" aria-label="Flight price chart" />;
}

function App() {
 const [from,setFrom]=useState('DEL'), [to,setTo]=useState('BOM'), [domain,setDomain]=useState('https://example.com');
 const [fares,setFares]=useState([]), [history,setHistory]=useState([]), [airlines,setAirlines]=useState([]), [model,setModel]=useState(null), [crawl,setCrawl]=useState(null), [loading,setLoading]=useState(false);
 const load = async () => { setLoading(true); try { const q=`origin=${from}&destination=${to}`; const [f,h,a,m]=await Promise.all(['/api/v1/fares','/api/v1/fares/history','/api/v1/analytics/airlines','/api/v1/model/status'].map(p=>fetch(`${API}${p}?${q}`).then(r=>r.json()))); setFares(f);setHistory(h);setAirlines(a);setModel(m); } finally {setLoading(false)} };
 useEffect(()=>{load()},[]);
 const scrape = async () => { setCrawl({status:'building sitemap'}); const res=await fetch(`${API}/api/v1/scrape`,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({domain,origin:from,destination:to,max_pages:5})}); setCrawl(await res.json()); };
 const chartData = history.length ? [{x:history.map(r=>r.date),y:history.map(r=>r.average_fare),name:'Average fare'}] : [];
 return <main><header><div><span className="eyebrow">SIH26056 / LIVE MARKET INTELLIGENCE</span><h1>Flight prices,<br/><em>made legible.</em></h1><p className="sub">Discover fare movement across India with transparent sources, structured extraction, and route-level signals.</p></div><div className="status"><span className="pulse"/> API ONLINE<br/><small>{loading?'Refreshing market':'Ready to search'}</small></div></header>
 <section className="search"><div><label>FROM</label><select value={from} onChange={e=>setFrom(e.target.value)}>{airports.map(a=><option key={a}>{a}</option>)}</select></div><span className="arrow">→</span><div><label>TO</label><select value={to} onChange={e=>setTo(e.target.value)}>{airports.filter(a=>a!==from).map(a=><option key={a}>{a}</option>)}</select></div><div className="domain"><label>PERMITTED SOURCE DOMAIN</label><input value={domain} onChange={e=>setDomain(e.target.value)} placeholder="https://airline.example"/></div><button onClick={load}>Search fares</button><button className="secondary" onClick={scrape}>Build sitemap + crawl</button></section>
 {model && !model.available && <div className="warning">Local model unavailable. Run <code>ollama pull {model.model}</code> before enabling LLM cleanup.</div>}
 {crawl && <div className="crawl"><strong>{crawl.status}</strong> <span>{crawl.message || `${crawl.urls?.length || 0} sitemap URLs prepared`}</span></div>}
 <section className="metrics"><div><small>ROUTE</small><strong>{from} → {to}</strong><span>Domestic market</span></div><div><small>FLIGHTS FOUND</small><strong>{fares.length}</strong><span>Structured records</span></div><div><small>LOWEST FARE</small><strong>{fares.length?money(Math.min(...fares.map(f=>f.total_fare))):'—'}</strong><span>Including taxes</span></div><div><small>MODEL</small><strong>{model?.available?'Llama 3.1':'Offline'}</strong><span>{model?.available?'Ready for cleanup':'Fallback active'}</span></div></section>
 <section className="grid"><article><div className="cardhead"><div><small>FARE MOVEMENT / 30 DAYS</small><h2>Route price history</h2></div><span className="tag">PLOTLY</span></div><Chart data={chartData} x="x" y="y"/></article><article><div className="cardhead"><div><small>AIRLINE BENCHMARK</small><h2>Compare carriers</h2></div></div><Chart data={airlines.map(a=>({...a,name:a.airline}))} type="bar" x="airline" y="average_fare"/></article></section>
 <section className="results"><div className="cardhead"><div><small>BOOKABLE RESULTS / {from}-{to}</small><h2>Available flights</h2></div><span className="tag">HASHED + DEDUPED</span></div>{fares.map(f=><div className="flight" key={f.id}><div className="airline"><b>{f.airline}</b><span>{f.flight_number}</span></div><div><b>{f.departure} — {f.arrival}</b><span>{f.duration} · {f.stops?'Stops':'Non-stop'}</span></div><div><b>{money(f.total_fare)}</b><span>{f.availability} seats left</span></div><a href={f.booking_url} target="_blank" rel="noreferrer">Book flight ↗</a></div>)}</section><footer>Sources are crawled only when permitted. Never bypass robots.txt, authentication, CAPTCHAs, or access controls.</footer></main>
}
createRoot(document.getElementById('root')).render(<App/>);
