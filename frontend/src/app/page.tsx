"use client";

import { useEffect, useRef, useState } from "react";

const STATS = [
  { value: 32, suffix: "M", label: "Hectáreas agrícolas en Colombia" },
  { value: 78, suffix: "%", label: "Municipios con riesgo climático" },
  { value: 12, suffix: "M", label: "Familias rurales afectadas" },
  { value: 4, suffix: "x", label: "Más rápido que modelos tradicionales" },
];

const FEATURES = [
  {
    icon: "🌦",
    tag: "01",
    title: "Predicción de Riesgo",
    desc: "Modelos ML entrenados con datos IDEAM, NASA POWER y OpenWeather para anticipar sequías, inundaciones y heladas con días de anticipación.",
    color: "#dcfce7",
    accent: "#16a34a",
  },
  {
    icon: "🗺",
    tag: "02",
    title: "Mapa en Tiempo Real",
    desc: "Visualización geoespacial de riesgos por departamento y municipio con capas de variables climáticas interactivas.",
    color: "#dbeafe",
    accent: "#2563eb",
  },
  {
    icon: "🔔",
    tag: "03",
    title: "Alertas Inteligentes",
    desc: "Notificaciones automáticas para comunidades rurales y entes gubernamentales antes de que ocurran los eventos críticos.",
    color: "#fef9c3",
    accent: "#ca8a04",
  },
  {
    icon: "📊",
    tag: "04",
    title: "Datos Abiertos",
    desc: "Integración con datos.gov.co, DANE, IDEAM y APIs internacionales para garantizar transparencia total y trazabilidad.",
    color: "#fce7f3",
    accent: "#db2777",
  },
];

function Counter({ target, suffix }: { target: number; suffix: string }) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const started = useRef(false);
  useEffect(() => {
    const observer = new IntersectionObserver(([e]) => {
      if (e.isIntersecting && !started.current) {
        started.current = true;
        let start = 0;
        const step = (ts: number) => {
          if (!start) start = ts;
          const p = Math.min((ts - start) / 1600, 1);
          setCount(Math.floor((1 - Math.pow(1 - p, 3)) * target));
          if (p < 1) requestAnimationFrame(step);
          else setCount(target);
        };
        requestAnimationFrame(step);
      }
    }, { threshold: 0.3 });
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [target]);
  return <span ref={ref}>{count}{suffix}</span>;
}

export default function LandingPage() {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const h = () => setScrolled(window.scrollY > 30);
    window.addEventListener("scroll", h);
    return () => window.removeEventListener("scroll", h);
  }, []);

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
          --bg: #f8f9f6;
          --white: #ffffff;
          --ink: #111612;
          --ink2: #3d4a41;
          --muted: #8a9e90;
          --border: #e2e8e4;
          --green: #16a34a;
          --green-light: #dcfce7;
          --ff-serif: 'Instrument Serif', Georgia, serif;
          --ff-sans: 'Inter', sans-serif;
          --ff-mono: 'JetBrains Mono', monospace;
        }

        html { scroll-behavior: smooth; }
        body {
          background: var(--bg);
          color: var(--ink);
          font-family: var(--ff-sans);
          font-size: 15px;
          line-height: 1.6;
          overflow-x: hidden;
        }

        nav {
          position: fixed; top: 0; left: 0; right: 0; z-index: 100;
          display: flex; align-items: center; justify-content: space-between;
          padding: 1.25rem 3rem;
          transition: all 0.3s;
        }
        nav.scrolled {
          background: rgba(248,249,246,0.94);
          border-bottom: 1px solid var(--border);
          backdrop-filter: blur(16px);
          padding: 0.85rem 3rem;
        }
        .nav-logo {
          font-family: var(--ff-sans); font-weight: 600;
          font-size: 1rem; letter-spacing: -0.02em;
          color: var(--ink); text-decoration: none;
          display: flex; align-items: center; gap: 0.5rem;
        }
        .nav-badge {
          background: var(--green); color: #fff;
          font-size: 0.58rem; font-weight: 600;
          letter-spacing: 0.06em; padding: 0.15rem 0.45rem;
          border-radius: 4px;
        }
        .nav-links { display: flex; gap: 2rem; list-style: none; }
        .nav-links a { font-size: 0.85rem; color: var(--ink2); text-decoration: none; transition: color 0.2s; }
        .nav-links a:hover { color: var(--ink); }
        .nav-cta {
          background: var(--ink); color: #fff;
          font-size: 0.8rem; font-weight: 500;
          padding: 0.6rem 1.4rem; border-radius: 8px;
          text-decoration: none; transition: opacity 0.2s;
        }
        .nav-cta:hover { opacity: 0.8; }

        .hero {
          min-height: 100vh;
          display: grid; grid-template-columns: 1fr 1fr;
          align-items: center;
          padding: 7rem 3rem 4rem;
          gap: 5rem;
          max-width: 1400px; margin: 0 auto;
        }
        .hero-eyebrow {
          display: inline-flex; align-items: center; gap: 0.5rem;
          background: var(--green-light); color: var(--green);
          font-size: 0.72rem; font-weight: 600; letter-spacing: 0.05em;
          text-transform: uppercase; padding: 0.35rem 0.85rem;
          border-radius: 100px; margin-bottom: 1.75rem;
        }
        .hero-eyebrow::before { content: '●'; font-size: 0.45rem; }
        h1 {
          font-family: var(--ff-serif);
          font-size: clamp(3rem, 5vw, 5.2rem);
          line-height: 1.08; letter-spacing: -0.02em;
          color: var(--ink); margin-bottom: 1.5rem; font-weight: 400;
        }
        h1 em { font-style: italic; color: var(--green); }
        .hero-desc {
          font-size: 1.05rem; line-height: 1.75;
          color: var(--ink2); margin-bottom: 2.5rem; max-width: 460px;
        }
        .hero-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }
        .btn-primary {
          background: var(--green); color: #fff;
          font-size: 0.875rem; font-weight: 500;
          padding: 0.85rem 1.75rem; border-radius: 10px;
          text-decoration: none; display: inline-flex; align-items: center; gap: 0.5rem;
          transition: background 0.2s, transform 0.15s;
        }
        .btn-primary:hover { background: #15803d; transform: translateY(-1px); }
        .btn-ghost {
          background: var(--white); color: var(--ink);
          font-size: 0.875rem; font-weight: 500;
          padding: 0.85rem 1.75rem; border-radius: 10px;
          text-decoration: none; border: 1px solid var(--border);
          transition: border-color 0.2s, transform 0.15s;
        }
        .btn-ghost:hover { border-color: var(--ink2); transform: translateY(-1px); }

        .hero-visual {
          background: var(--white); border: 1px solid var(--border);
          border-radius: 20px; padding: 1.75rem;
          box-shadow: 0 4px 40px rgba(0,0,0,0.07);
        }
        .visual-header {
          display: flex; align-items: center; gap: 0.45rem;
          margin-bottom: 1.5rem; padding-bottom: 1rem;
          border-bottom: 1px solid var(--border);
        }
        .dot { width: 10px; height: 10px; border-radius: 50%; }
        .dr{background:#ff5f57}.dy{background:#febc2e}.dg{background:#28c840}
        .visual-label {
          font-family: var(--ff-mono); font-size: 0.65rem;
          color: var(--muted); margin-left: auto;
        }
        .risk-row {
          display: flex; align-items: center; gap: 0.85rem;
          padding: 0.85rem 1rem; border-radius: 10px;
          margin-bottom: 0.5rem; border: 1px solid var(--border);
          transition: box-shadow 0.2s;
        }
        .risk-row:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
        .rbadge {
          font-size: 0.62rem; font-weight: 600; letter-spacing: 0.06em;
          text-transform: uppercase; padding: 0.22rem 0.6rem; border-radius: 6px;
          white-space: nowrap;
        }
        .rc { background:#fee2e2; color:#dc2626; }
        .rh { background:#ffedd5; color:#ea580c; }
        .rm { background:#fef9c3; color:#ca8a04; }
        .rl { background:#dcfce7; color:#16a34a; }
        .rname { font-weight: 500; font-size: 0.875rem; flex: 1; }
        .rtype { font-size: 0.72rem; color: var(--muted); }
        .rconf { font-family: var(--ff-mono); font-size: 0.68rem; color: var(--muted); }
        .visual-foot {
          margin-top: 0.75rem; padding-top: 0.75rem;
          border-top: 1px solid var(--border);
          display: flex; align-items: center; gap: 0.45rem;
          font-family: var(--ff-mono); font-size: 0.62rem; color: var(--muted);
        }
        .ldot {
          width: 7px; height: 7px; border-radius: 50%;
          background: var(--green);
          animation: blink 2s ease-in-out infinite;
        }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

        .stats-strip { background: var(--white); border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); }
        .stats-inner { max-width: 1400px; margin: 0 auto; display: grid; grid-template-columns: repeat(4,1fr); }
        .stat-item { padding: 2.5rem 3rem; border-right: 1px solid var(--border); }
        .stat-item:last-child { border-right: none; }
        .stat-num {
          font-family: var(--ff-serif); font-size: 3rem; line-height: 1;
          color: var(--green); display: block; margin-bottom: 0.4rem; font-weight: 400;
        }
        .stat-lbl { font-size: 0.78rem; color: var(--muted); line-height: 1.4; }

        .sw { max-width: 1400px; margin: 0 auto; padding: 6rem 3rem; }
        .eyebrow {
          display: inline-flex; align-items: center; gap: 0.4rem;
          font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em;
          text-transform: uppercase; color: var(--muted); margin-bottom: 1rem;
        }
        .eyebrow::before { content: '—'; }
        h2 {
          font-family: var(--ff-serif);
          font-size: clamp(2.2rem, 4vw, 3.6rem);
          font-weight: 400; line-height: 1.1; letter-spacing: -0.02em; margin-bottom: 1.25rem;
        }
        .sdesc { font-size: 1rem; color: var(--ink2); line-height: 1.75; max-width: 500px; }

        .fw { background: var(--white); }
        .fheader { display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: end; margin-bottom: 3.5rem; }
        .fgrid { display: grid; grid-template-columns: repeat(2,1fr); gap: 1.25rem; }
        .fcard { border-radius: 16px; padding: 2rem; transition: transform 0.2s, box-shadow 0.2s; }
        .fcard:hover { transform: translateY(-3px); box-shadow: 0 8px 32px rgba(0,0,0,0.08); }
        .ftop { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.25rem; }
        .ficon { font-size: 1.75rem; }
        .ftag { font-family: var(--ff-mono); font-size: 0.62rem; color: var(--muted); }
        .ftitle { font-weight: 600; font-size: 0.95rem; margin-bottom: 0.5rem; }
        .fdesc { font-size: 0.83rem; color: var(--ink2); line-height: 1.65; }

        .sgrid { display: grid; grid-template-columns: repeat(4,1fr); gap: 1.25rem; margin-top: 3rem; }
        .scard {
          background: var(--white); border: 1px solid var(--border);
          border-radius: 14px; padding: 1.75rem; transition: box-shadow 0.2s;
        }
        .scard:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.07); }
        .slayer { font-size: 0.62rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); margin-bottom: 0.75rem; }
        .sname { font-family: var(--ff-serif); font-size: 1.6rem; line-height: 1; margin-bottom: 0.75rem; }
        .spills { display: flex; flex-wrap: wrap; gap: 0.35rem; }
        .pill { font-size: 0.68rem; font-weight: 500; background: var(--bg); color: var(--ink2); border: 1px solid var(--border); padding: 0.18rem 0.55rem; border-radius: 100px; }

        .ctaw {
          background: var(--ink); color: #fff;
          border-radius: 24px; margin: 0 3rem 5rem;
          padding: 5rem; text-align: center; position: relative; overflow: hidden;
        }
        .ctaglow {
          position: absolute; top: -60%; left: 50%; transform: translateX(-50%);
          width: 700px; height: 400px;
          background: radial-gradient(ellipse, rgba(34,197,94,0.12) 0%, transparent 70%);
          pointer-events: none;
        }
        .ctaw h2 { color: #fff; position: relative; margin-bottom: 1rem; }
        .ctaw h2 em { color: #4ade80; }
        .ctasub { color: rgba(255,255,255,0.45); margin-bottom: 2.5rem; position: relative; }
        .btnw {
          background: #fff; color: var(--ink);
          font-size: 0.9rem; font-weight: 600;
          padding: 0.9rem 2.2rem; border-radius: 10px;
          text-decoration: none; display: inline-block;
          transition: opacity 0.2s, transform 0.15s; position: relative;
        }
        .btnw:hover { opacity: 0.9; transform: translateY(-1px); }

        footer {
          border-top: 1px solid var(--border); padding: 2rem 3rem;
          display: flex; justify-content: space-between; align-items: center;
          max-width: 1400px; margin: 0 auto;
        }
        .flogo { font-weight: 600; font-size: 0.9rem; letter-spacing: -0.01em; }
        .flogo span { color: var(--green); }
        .fcopy { font-size: 0.75rem; color: var(--muted); }
        .schip {
          display: inline-flex; align-items: center; gap: 0.4rem;
          background: var(--green-light); color: var(--green);
          font-size: 0.68rem; font-weight: 600;
          padding: 0.28rem 0.75rem; border-radius: 100px;
        }
        .schip::before { content:''; width:6px; height:6px; border-radius:50%; background:var(--green); animation: blink 2s ease-in-out infinite; }

        @media(max-width:900px){
          nav{padding:1rem 1.5rem}
          nav.scrolled{padding:.7rem 1.5rem}
          .nav-links{display:none}
          .hero{grid-template-columns:1fr;padding:6rem 1.5rem 3rem;gap:3rem}
          .stats-inner{grid-template-columns:repeat(2,1fr)}
          .stat-item:nth-child(2){border-right:none}
          .stat-item{padding:2rem 1.5rem}
          .sw{padding:4rem 1.5rem}
          .fheader{grid-template-columns:1fr;gap:2rem}
          .fgrid{grid-template-columns:1fr}
          .sgrid{grid-template-columns:repeat(2,1fr)}
          .ctaw{margin:0 1.5rem 4rem;padding:3rem 2rem}
          footer{flex-direction:column;gap:1rem;text-align:center}
        }
      `}</style>

      <nav className={scrolled ? "scrolled" : ""}>
        <a href="#" className="nav-logo">
          IA Colombia <span className="nav-badge">BETA</span>
        </a>
        <ul className="nav-links">
          <li><a href="#features">Módulos</a></li>
          <li><a href="#stack">Stack</a></li>
          <li><a href="#stack">Datos</a></li>
        </ul>
        <a href="/dashboard" className="nav-cta">Abrir Dashboard →</a>
      </nav>

      <div style={{ maxWidth: 1400, margin: "0 auto" }}>
        <div className="hero">
          <div>
            <div className="hero-eyebrow">Plataforma IA · Colombia 2026</div>
            <h1>Datos que<br /><em>protegen</em><br />el campo</h1>
            <p className="hero-desc">
              Inteligencia artificial aplicada a la agricultura y el desarrollo sostenible.
              Predicción de riesgos climáticos con datos abiertos del territorio colombiano.
            </p>
            <div className="hero-actions">
              <a href="/dashboard" className="btn-primary">Ver Dashboard →</a>
              <a href="#features" className="btn-ghost">Conocer más</a>
            </div>
          </div>

          <div className="hero-visual">
            <div className="visual-header">
              <div className="dot dr"/><div className="dot dy"/><div className="dot dg"/>
              <span className="visual-label">panel de riesgos · en vivo</span>
            </div>
            {[
              { region:"La Guajira", type:"Sequía",      lvl:"rc", label:"crítico", conf:"92%" },
              { region:"Chocó",      type:"Inundación",  lvl:"rh", label:"alto",    conf:"87%" },
              { region:"Córdoba",    type:"Inundación",  lvl:"rh", label:"alto",    conf:"81%" },
              { region:"Antioquia",  type:"Sequía",      lvl:"rm", label:"medio",   conf:"74%" },
              { region:"Cundinamarca",type:"Helada",     lvl:"rl", label:"bajo",    conf:"61%" },
            ].map(r => (
              <div key={r.region} className="risk-row">
                <span className={`rbadge ${r.lvl}`}>{r.label}</span>
                <div style={{flex:1}}>
                  <div className="rname">{r.region}</div>
                  <div className="rtype">{r.type}</div>
                </div>
                <div className="rconf">{r.conf}</div>
              </div>
            ))}
            <div className="visual-foot">
              <div className="ldot"/>
              Actualizado hace 2 min · IDEAM + OpenWeather
            </div>
          </div>
        </div>
      </div>

      <div className="stats-strip">
        <div className="stats-inner">
          {STATS.map(s => (
            <div key={s.label} className="stat-item">
              <span className="stat-num"><Counter target={s.value} suffix={s.suffix}/></span>
              <span className="stat-lbl">{s.label}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="fw" id="features">
        <div className="sw">
          <div className="fheader">
            <div>
              <div className="eyebrow">Módulos</div>
              <h2>Todo lo que necesita una plataforma de riesgo climático</h2>
            </div>
            <p className="sdesc">
              Cuatro módulos integrados que cubren el ciclo completo: datos → análisis → predicción → acción.
            </p>
          </div>
          <div className="fgrid">
            {FEATURES.map(f => (
              <div key={f.title} className="fcard" style={{background: f.color}}>
                <div className="ftop">
                  <span className="ficon">{f.icon}</span>
                  <span className="ftag">{f.tag}</span>
                </div>
                <div className="ftitle" style={{color: f.accent}}>{f.title}</div>
                <div className="fdesc">{f.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div id="stack">
        <div className="sw">
          <div className="eyebrow">Tecnología</div>
          <h2>Stack moderno,<br />arquitectura sólida</h2>
          <div className="sgrid">
            {[
              { layer:"Frontend", name:"Next.js",  pills:["TypeScript","TailwindCSS","Recharts","Leaflet"] },
              { layer:"Backend",  name:"NestJS",   pills:["Prisma ORM","PostgreSQL","JWT Auth","Swagger"] },
              { layer:"IA",       name:"FastAPI",  pills:["Scikit-learn","Pandas","NumPy","Python 3.11"] },
              { layer:"DevOps",   name:"Docker",   pills:["Compose","PostgreSQL 16","GitHub CI"] },
            ].map(s => (
              <div key={s.name} className="scard">
                <div className="slayer">{s.layer}</div>
                <div className="sname">{s.name}</div>
                <div className="spills">{s.pills.map(p => <span key={p} className="pill">{p}</span>)}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="ctaw">
        <div className="ctaglow"/>
        <h2>Explora el <em>mapa</em><br />de riesgos de Colombia</h2>
        <p className="ctasub" style={{marginTop:"1rem"}}>
          Visualiza en tiempo real los riesgos climáticos de cada región del país.
        </p>
        <a href="/dashboard" className="btnw">Abrir Dashboard completo →</a>
      </div>

      <footer>
        <div className="flogo">IA <span>Colombia</span></div>
        <div className="schip">Sistemas operativos</div>
        <div className="fcopy">© 2026 · Datos abiertos · Hecho en Colombia 🇨🇴</div>
      </footer>
    </>
  );
}