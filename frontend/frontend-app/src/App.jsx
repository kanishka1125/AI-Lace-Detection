import React, { useState, useEffect, useRef, useMemo } from "react";
import {
  Search, Image as ImageIcon, Type, Upload, Camera, X, Menu, Home as HomeIcon,
  LayoutGrid, Info, ChevronRight, ChevronLeft, Download, Eye, Loader2, SlidersHorizontal,
  ArrowLeft, Sparkles, Ruler, Layers, Grid3x3, Check, ScanSearch,
  Gauge, ShieldCheck, Zap, Clock, Database, Cpu, Target, Calendar, CheckCircle2,
  History, RotateCcw, ArrowUpRight,
} from "lucide-react";

/* ---------------------------------------------------------------------- */
/*  Fonts — modern sans-serif stack, no redesign, just typography polish   */
/* ---------------------------------------------------------------------- */

function FontLoader() {
  useEffect(() => {
    const id = "afl-fonts";
    if (document.getElementById(id)) return;
    const link = document.createElement("link");
    link.id = id;
    link.rel = "stylesheet";
    link.href =
      "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap";
    document.head.appendChild(link);
  }, []);
  return null;
}

const FONT_STACK = "'Inter','SF Pro Display','Geist','Manrope',ui-sans-serif,system-ui,-apple-system,sans-serif";
const fontDisplay = { fontFamily: FONT_STACK, fontWeight: 600, letterSpacing: "-0.02em" };
const fontBody = { fontFamily: FONT_STACK };

/* ---------------------------------------------------------------------- */
/*  Mock data                                                              */
/* ---------------------------------------------------------------------- */

const CATEGORY_META = {
  Lace: { dot: "bg-red-500", label: "Lace", text: "text-red-700", bg: "bg-red-50", border: "border-red-200", glow: "#EF4444" },
  Fabric: { dot: "bg-green-500", label: "Fabric", text: "text-green-700", bg: "bg-green-50", border: "border-green-200", glow: "#22C55E" },
  Other: { dot: "bg-blue-500", label: "Other", text: "text-blue-700", bg: "bg-blue-50", border: "border-blue-200", glow: "#3B82F6" },
};

const API_BASE_URL = "http://127.0.0.1:8000";

function catalogueImageUrl(path) {
  const raw = String(path || "").replace(/\\/g, "/");
  if (!raw) return "";
  if (raw.startsWith("http://") || raw.startsWith("https://")) return raw;
  return `${API_BASE_URL}${raw.startsWith("/") ? "" : "/"}${raw}`;
}

function normalizeCatalogueProduct(item, index = 0) {
  const productId = item?.product_id || `PRODUCT-${index + 1}`;
  return {
    id: productId,
    sku: productId,
    name: item?.name || productId,
    category: item?.category || "Lace",
    material: item?.material || "—",
    pattern: item?.pattern || "—",
    width: item?.width || "—",
    gsm: item?.gsm || "—",
    description: item?.description || "Catalogue product.",
    applications: Array.isArray(item?.applications) ? item.applications : [],
    imageUrl: catalogueImageUrl(item?.image),
  };
}

const PRODUCTS = [
  {
    id: "p1", sku: "LACE-2001", name: "White Floral Scallop Lace", category: "Lace",
    material: "Cotton / Nylon Blend", pattern: "Floral", patternType: "lace-floral",
    width: "130 cm", gsm: "85 gsm",
    description: "Delicate white floral lace with scalloped edges and a soft tulle mesh base, well suited to bridal veils and refined eveningwear.",
    applications: ["Bridal Wear", "Evening Wear"],
  },
  {
    id: "p2", sku: "LACE-2048", name: "White Floral Embroidered Lace", category: "Lace",
    material: "Nylon", pattern: "Floral Embroidery", patternType: "lace-floral",
    width: "135 cm", gsm: "90 gsm",
    description: "White embroidered floral lace with intricate leaf motifs and mesh backing, suitable for bridal and luxury garments.",
    applications: ["Bridal Wear", "Fashion Apparel"],
  },
  {
    id: "p3", sku: "LACE-2102", name: "Black Chantilly Scroll Lace", category: "Lace",
    material: "Polyester", pattern: "Scroll Floral", patternType: "lace-floral",
    width: "150 cm", gsm: "95 gsm",
    description: "Rich black Chantilly-style lace with scrolling floral embroidery, offering dramatic contrast for evening gowns and overlays.",
    applications: ["Evening Wear", "Fashion Apparel"],
  },
  {
    id: "p4", sku: "LACE-2159", name: "Ivory Guipure Cutwork Lace", category: "Lace",
    material: "Cotton", pattern: "Guipure Motif", patternType: "lace-guipure",
    width: "45 cm", gsm: "60 gsm",
    description: "Ivory guipure lace with bold cutwork motifs and a sturdy cotton base, well suited to structured bridal bodices.",
    applications: ["Bridal Wear"],
  },
  {
    id: "p5", sku: "LACE-2210", name: "Blush Corded Net Lace", category: "Lace",
    material: "Nylon", pattern: "Corded Floral", patternType: "lace-corded",
    width: "130 cm", gsm: "80 gsm",
    description: "Soft blush lace with corded floral outlines over a fine net ground, lending a romantic finish to occasion wear.",
    applications: ["Evening Wear", "Fashion Apparel"],
  },
  {
    id: "p6", sku: "LACE-2305", name: "Champagne Beaded Lattice Lace", category: "Lace",
    material: "Polyester / Nylon", pattern: "Beaded Floral", patternType: "lace-beaded",
    width: "140 cm", gsm: "110 gsm",
    description: "Champagne lace embellished with hand-placed beading across a floral lattice, designed for statement eveningwear.",
    applications: ["Evening Wear", "Bridal Wear"],
  },
  {
    id: "p7", sku: "FAB-1020", name: "Black Cotton Fabric", category: "Fabric",
    material: "Cotton", pattern: "Solid", patternType: "solid",
    width: "150 cm", gsm: "180 gsm",
    description: "Densely woven black cotton fabric with a smooth matte finish, dependable for tailored apparel and structured linings.",
    applications: ["Fashion Apparel"],
  },
  {
    id: "p8", sku: "FAB-1105", name: "Ivory Silk Charmeuse", category: "Fabric",
    material: "Silk", pattern: "Satin Weave", patternType: "solid",
    width: "114 cm", gsm: "60 gsm",
    description: "Fluid ivory silk charmeuse with a lustrous drape, favored for bias-cut gowns and luxury lingerie.",
    applications: ["Bridal Wear", "Evening Wear"],
  },
  {
    id: "p9", sku: "FAB-1210", name: "Navy Stretch Mesh Fabric", category: "Fabric",
    material: "Nylon / Spandex", pattern: "Mesh", patternType: "mesh",
    width: "150 cm", gsm: "90 gsm",
    description: "Four-way stretch navy mesh with a fine open weave, suited to activewear linings and layered eveningwear.",
    applications: ["Fashion Apparel", "Evening Wear"],
  },
  {
    id: "p10", sku: "FAB-1315", name: "Rose Gold Metallic Organza", category: "Fabric",
    material: "Polyester", pattern: "Sheen Solid", patternType: "solid",
    width: "112 cm", gsm: "45 gsm",
    description: "Rose gold organza with a crisp hand and subtle metallic sheen, adding structure and shimmer to eveningwear silhouettes.",
    applications: ["Evening Wear"],
  },
  {
    id: "p11", sku: "FAB-1420", name: "Charcoal Wool Blend Suiting", category: "Fabric",
    material: "Wool / Polyester", pattern: "Herringbone", patternType: "herringbone",
    width: "150 cm", gsm: "260 gsm",
    description: "Charcoal wool-blend suiting in a fine herringbone weave, tailored for structured jackets and outerwear.",
    applications: ["Fashion Apparel"],
  },
  {
    id: "p12", sku: "FAB-1512", name: "Emerald Velvet Fabric", category: "Fabric",
    material: "Polyester Pile", pattern: "Solid Velvet", patternType: "velvet",
    width: "140 cm", gsm: "320 gsm",
    description: "Deep emerald velvet with a dense, light-catching pile, chosen for opulent eveningwear and upholstered home accents.",
    applications: ["Evening Wear", "Home Decor"],
  },
  {
    id: "p13", sku: "ACC-201", name: "Decorative Pearl Trim", category: "Other",
    material: "Pearl / Cotton Tape", pattern: "Beaded", patternType: "sequin",
    width: "2 cm", gsm: "30 gsm",
    description: "Hand-strung pearl trim on a cotton tape base, used to finish necklines and bridal accessories with subtle shine.",
    applications: ["Bridal Wear"],
  },
  {
    id: "p14", sku: "ACC-215", name: "Burgundy Satin Ribbon Trim", category: "Other",
    material: "Polyester Satin", pattern: "Solid", patternType: "solid",
    width: "2.5 cm", gsm: "25 gsm",
    description: "Lustrous burgundy satin ribbon with a smooth double face, suited to sashes, trims and gift packaging.",
    applications: ["Fashion Apparel", "Home Decor"],
  },
  {
    id: "p15", sku: "ACC-230", name: "Gold Sequin Fringe Trim", category: "Other",
    material: "Polyester Sequin", pattern: "Sequined", patternType: "sequin",
    width: "5 cm", gsm: "50 gsm",
    description: "Gold sequin fringe trim with continuous shimmer and movement, popular for dancewear and statement hemlines.",
    applications: ["Evening Wear", "Fashion Apparel"],
  },
];

/* ---------------------------------------------------------------------- */
/*  Deterministic pseudo-random helper (seeded by SKU)                     */
/* ---------------------------------------------------------------------- */

function seedFromString(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) >>> 0;
  return h;
}
function mulberry32(seed) {
  let a = seed;
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function similarityColor(v) {
  const n = Number(v);
  if (n >= 95) return { bar: "#22C55E", text: "text-green-700", bg: "bg-green-50", border: "border-green-200" };
  if (n >= 85) return { bar: "#3B82F6", text: "text-blue-700", bg: "bg-blue-50", border: "border-blue-200" };
  if (n >= 70) return { bar: "#EAB308", text: "text-yellow-700", bg: "bg-yellow-50", border: "border-yellow-200" };
  return { bar: "#EF4444", text: "text-red-700", bg: "bg-red-50", border: "border-red-200" };
}

/* ---------------------------------------------------------------------- */
/*  Swatch — procedurally rendered fabric/lace texture                     */
/* ---------------------------------------------------------------------- */

function textColorFor(hex) {
  if (!hex) return "#ffffff";

  const c = hex.replace("#", "");
  const r = parseInt(c.substring(0, 2), 16);
  const g = parseInt(c.substring(2, 4), 16);
  const b = parseInt(c.substring(4, 6), 16);
  const lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

  return lum > 0.6 ? "#000000" : "#ffffff";
}

function Swatch({ product, className = "" }) {
  return (
    <div className={`relative overflow-hidden bg-gray-50 ${className}`}>
      {product.imageUrl ? (
        <img
          src={product.imageUrl}
          alt={product.name || product.sku}
          className="w-full h-full object-cover"
          onError={(e) => {
            console.error("Image failed to load:", product.imageUrl);
            e.currentTarget.style.display = "none";
          }}
        />
      ) : (
        <div className="w-full h-full flex items-center justify-center text-gray-400">
          No image
        </div>
      )}

      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          boxShadow: "inset 0 0 60px rgba(0,0,0,0.06)",
        }}
      />
    </div>
  );
}

/* ---------------------------------------------------------------------- */
/*  Button — premium, rounded, loading / disabled / ripple                 */
/* ---------------------------------------------------------------------- */

function Btn({ as: As = "button", variant = "primary", size = "md", loading = false, disabled = false, icon: Icon, className = "", children, onClick, ...rest }) {
  const [ripples, setRipples] = useState([]);

  const base = "relative overflow-hidden inline-flex items-center justify-center gap-2 font-medium select-none transition-all duration-200 ease-out focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 focus-visible:ring-offset-2 disabled:opacity-40 disabled:cursor-not-allowed active:scale-[0.98]";
  const sizes = { sm: "text-xs px-3 py-2 rounded-lg", md: "text-sm px-4 py-2.5 rounded-xl", lg: "text-sm px-5 py-3.5 rounded-2xl" };
  const variants = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 shadow-sm hover:shadow-md hover:shadow-blue-200",
    secondary: "bg-white text-gray-700 border border-gray-200 hover:bg-gray-50 hover:border-gray-300",
    ghost: "text-gray-600 hover:bg-gray-50",
    dark: "bg-gray-900 text-white hover:bg-black",
  };

  function handleClick(e) {
    if (disabled || loading) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const id = Date.now();
    setRipples((r) => [...r, { id, x: e.clientX - rect.left, y: e.clientY - rect.top, size: Math.max(rect.width, rect.height) * 1.6 }]);
    setTimeout(() => setRipples((r) => r.filter((rp) => rp.id !== id)), 600);
    onClick && onClick(e);
  }

  return (
    <As
      className={`${base} ${sizes[size]} ${variants[variant]} ${className}`}
      disabled={disabled || loading}
      onClick={handleClick}
      {...rest}
    >
      {ripples.map((r) => (
        <span
          key={r.id}
          className="absolute rounded-full bg-white/40 pointer-events-none animate-ripple"
          style={{ left: r.x - r.size / 2, top: r.y - r.size / 2, width: r.size, height: r.size }}
        />
      ))}
      {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : Icon ? <Icon className="w-4 h-4" /> : null}
      <span className="relative">{children}</span>
    </As>
  );
}

/* ---------------------------------------------------------------------- */
/*  Small shared UI pieces                                                 */
/* ---------------------------------------------------------------------- */

function CategoryDot({ category, className = "" }) {
  const meta = CATEGORY_META[category] || CATEGORY_META.Other;
  return <span className={`inline-block w-2.5 h-2.5 rounded-full ${meta.dot} ${className}`} />;
}

function CategoryBadge({ category }) {
  const m = CATEGORY_META[category] || CATEGORY_META.Other;
  return (
    <span className={`inline-flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide px-2.5 py-1 rounded-full bg-white/90 backdrop-blur-sm border border-white/60 shadow-sm ${m.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${m.dot}`} />
      {m.label}
    </span>
  );
}

function SimilarityBadge({ value }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-white/90 backdrop-blur-sm text-gray-900 text-[11px] font-semibold px-2.5 py-1 border border-white/60 shadow-sm">
      <Sparkles className="w-3 h-3 text-blue-600" />
      {value}%
    </span>
  );
}

function SimilarityBar({ value, animate = true }) {
  const [width, setWidth] = useState(0);
  const c = similarityColor(value);
  useEffect(() => {
    if (!animate) { setWidth(Number(value)); return; }
    const t = setTimeout(() => setWidth(Number(value)), 80);
    return () => clearTimeout(t);
  }, [value, animate]);
  return (
    <div className="h-1.5 w-full rounded-full bg-gray-100 overflow-hidden">
      <div
        className="h-full rounded-full transition-all duration-[900ms] ease-out"
        style={{ width: `${width}%`, backgroundColor: c.bar }}
      />
    </div>
  );
}

function AttributeGrid({ product, compact = false }) {
  const attrs = [
    { icon: Layers, label: "Material", value: product.material },
    { icon: Grid3x3, label: "Pattern", value: product.pattern },
    { icon: Ruler, label: "Width", value: product.width },
    { icon: Gauge, label: "GSM", value: product.gsm },
  ];
  return (
    <div className={`grid ${compact ? "grid-cols-2" : "grid-cols-2 sm:grid-cols-3 md:grid-cols-5"} gap-3`}>
      {attrs.map((a) => (
        <div key={a.label} className="rounded-xl border border-gray-200 bg-gray-50 px-3 py-2.5">
          <div className="flex items-center gap-1.5 text-gray-500 text-xs mb-1">
            <a.icon className="w-3.5 h-3.5" />
            {a.label}
          </div>
          <div className="text-gray-900 text-sm font-medium truncate">{a.value}</div>
        </div>
      ))}
    </div>
  );
}

function SpecTable({ product }) {
  const rows = [
    { icon: Layers, label: "Material", value: product.material },
    { icon: Grid3x3, label: "Pattern", value: product.pattern },
    { icon: Ruler, label: "Width", value: product.width },
    { icon: Gauge, label: "GSM", value: product.gsm },
    { icon: Layers, label: "Category", value: product.category },
  ];
  return (
    <div className="rounded-2xl border border-gray-200 overflow-hidden">
      <table className="w-full text-sm">
        <tbody>
          {rows.map((r, i) => (
            <tr key={r.label} className={i % 2 === 1 ? "bg-gray-50/70" : "bg-white"}>
              <td className="px-4 py-3 text-gray-500 w-2/5">
                <span className="inline-flex items-center gap-2">
                  <r.icon className="w-3.5 h-3.5" /> {r.label}
                </span>
              </td>
              <td className="px-4 py-3 text-gray-900 font-medium">{r.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ---------------------------------------------------------------------- */
/*  Navbar                                                                  */
/* ---------------------------------------------------------------------- */

function Navbar({ page, goTo, mobileOpen, setMobileOpen }) {
  const links = [
    { key: "home", label: "Home" },
    { key: "catalogue", label: "Catalogue" },
    { key: "about", label: "About" },
  ];
  return (
    <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-5 md:px-8">
        <div className="flex items-center justify-between h-16">
          <button onClick={() => goTo("home")} className="flex items-center gap-2.5 group focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 rounded-lg">
            <span className="text-[15px] md:text-base font-semibold text-black tracking-tight" style={fontDisplay}>
              AI Fabric &amp; Lace <span className="hidden sm:inline">Visual Search</span>
            </span>
          </button>

          <nav className="hidden md:flex items-center gap-1">
            {links.map((l) => (
              <button
                key={l.key}
                onClick={() => goTo(l.key)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 ${
                  page === l.key ? "text-blue-600 bg-blue-50" : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                }`}
              >
                {l.label}
              </button>
            ))}
          </nav>

          <button
            className="md:hidden p-2 -mr-2 rounded-lg text-gray-700 hover:bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400"
            onClick={() => setMobileOpen((v) => !v)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      <div className={`md:hidden overflow-hidden transition-all duration-300 ease-out ${mobileOpen ? "max-h-52" : "max-h-0"}`}>
        <div className="px-5 pb-4 flex flex-col gap-1 border-t border-gray-100 pt-3">
          {links.map((l) => (
            <button
              key={l.key}
              onClick={() => { goTo(l.key); setMobileOpen(false); }}
              className={`text-left px-3 py-2.5 rounded-lg text-sm font-medium ${page === l.key ? "text-blue-600 bg-blue-50" : "text-gray-600"}`}
            >
              {l.label}
            </button>
          ))}
        </div>
      </div>
    </header>
  );
}

/* ---------------------------------------------------------------------- */
/*  Bottom mobile nav                                                       */
/* ---------------------------------------------------------------------- */

function BottomNav({ page, goTo }) {
  const items = [
    { key: "home", label: "Home", icon: HomeIcon },
    { key: "catalogue", label: "Catalogue", icon: LayoutGrid },
    { key: "about", label: "About", icon: Info },
  ];
  return (
    <div className="md:hidden fixed bottom-0 inset-x-0 z-40 bg-white/95 backdrop-blur-md border-t border-gray-200" style={{ paddingBottom: "env(safe-area-inset-bottom, 0px)" }}>
      <div className="flex items-stretch">
        {items.map((it) => {
          const active = page === it.key;
          return (
            <button
              key={it.key}
              onClick={() => goTo(it.key)}
              className="flex-1 flex flex-col items-center justify-center gap-1 py-2.5 min-h-[44px] focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 focus-visible:ring-inset"
            >
              <it.icon className={`w-5 h-5 ${active ? "text-blue-600" : "text-gray-400"}`} />
              <span className={`text-[11px] font-medium ${active ? "text-blue-600" : "text-gray-400"}`}>{it.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------------- */
/*  Skeleton card                                                           */
/* ---------------------------------------------------------------------- */

function SkeletonCard() {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white overflow-hidden">
      <div className="aspect-square afl-shimmer" />
      <div className="p-4 space-y-3">
        <div className="h-3 w-20 rounded-full afl-shimmer" />
        <div className="h-4 w-3/4 rounded-full afl-shimmer" />
        <div className="h-3 w-full rounded-full afl-shimmer" />
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------------- */
/*  Result card — redesigned: image-forward, hover overlay, mobile tap     */
/* ---------------------------------------------------------------------- */

function ResultCard({ product, onView, style }) {
  const [expanded, setExpanded] = useState(false);
  const meta = CATEGORY_META[product.category] || CATEGORY_META.Other;

  return (
    <div
      className="group relative rounded-2xl border border-gray-200 bg-white overflow-hidden transition-all duration-[250ms] ease-out hover:-translate-y-1 hover:shadow-xl focus-within:-translate-y-1 focus-within:shadow-xl animate-fade-in cursor-pointer"
      style={{ ...style, borderColor: undefined }}
      onMouseEnter={(e) => (e.currentTarget.style.borderColor = meta.glow)}
      onMouseLeave={(e) => (e.currentTarget.style.borderColor = "")}
      tabIndex={0}
      role="group"
      aria-label={`${product.name}, ${product.sku}`}
    >
      {/* soft category glow on hover */}
      <div
        className="pointer-events-none absolute -inset-px rounded-2xl opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 transition-opacity duration-[250ms]"
        style={{ boxShadow: `0 0 0 1px ${meta.glow}33, 0 8px 24px -4px ${meta.glow}40` }}
      />

      {/* image + overlay */}
      <div
        className="relative aspect-square"
        onClick={() => setExpanded((v) => !v)}
      >
        <Swatch product={product} className="w-full h-full transition-transform duration-[400ms] ease-out group-hover:scale-[1.04]" />

        <div className="absolute top-3 left-3"><CategoryBadge category={product.category} /></div>
        <div className="absolute top-3 right-3"><SimilarityBadge value={product.similarity} /></div>

        {/* hover / tap overlay — lower half only */}
        <div
          className={`absolute inset-x-0 bottom-0 h-[62%] bg-gradient-to-t from-black/85 via-black/70 to-black/0 backdrop-blur-[2px] text-white px-3.5 pt-6 pb-3.5 flex flex-col justify-end transition-transform duration-300 ease-out ${
            expanded ? "translate-y-0" : "translate-y-full group-hover:translate-y-0 group-focus-within:translate-y-0"
          }`}
        >
          <p className="text-[11px] font-semibold uppercase tracking-wide text-white/70 mb-1.5">Why this match?</p>
          <ul className="space-y-0.5 mb-2.5 text-[11px] leading-tight">
            {["Similar embroidery pattern", "Matching texture", "Similar border style", "Similar motif density"].map((r) => (
              <li key={r} className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3 h-3 text-green-400 flex-shrink-0" /> {r}
              </li>
            ))}
          </ul>

          <p className="text-[11px] font-semibold uppercase tracking-wide text-white/70 mb-1.5">Specifications</p>
          <div className="grid grid-cols-2 gap-3 text-xs text-gray-600">
            <div>
              <span className="font-medium">Pattern:</span>{" "}
              {product.pattern || "—"}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={(e) => { e.stopPropagation(); onView(product); }}
              className="flex items-center justify-center gap-1.5 text-[11px] font-semibold px-2.5 py-2 rounded-lg bg-white text-gray-900 hover:bg-gray-100 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
            >
              <Eye className="w-3.5 h-3.5" /> View Details
            </button>
            <button
              onClick={(e) => e.stopPropagation()}
              className="flex items-center justify-center gap-1.5 text-[11px] font-semibold px-2.5 py-2 rounded-lg bg-white/10 border border-white/30 text-white hover:bg-white/20 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
            >
              <Download className="w-3.5 h-3.5" /> Spec Sheet
            </button>
          </div>
        </div>
      </div>

      {/* default visible content */}
      <div className="p-4" onClick={() => onView(product)}>
        <SimilarityBar value={product.similarity} />
        <div className="text-[11px] font-medium text-gray-400 tracking-wide mt-3 mb-1">{product.sku}</div>
        <h3 className="text-[15px] font-semibold text-gray-900 mb-1 leading-snug tracking-tight" style={fontDisplay}>
          {product.name}
        </h3>
        <p className="text-[13px] text-gray-500 leading-relaxed truncate">{product.description}</p>
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------------- */
/*  Search analytics panel                                                  */
/* ---------------------------------------------------------------------- */

function SearchAnalyticsPanel({ analytics, imagePreview, tab }) {
  const metrics = [
    { icon: analytics.mode === "Image Search" ? ImageIcon : Type, label: "Search Mode", value: analytics.mode },
    { icon: Clock, label: "Search Time", value: `${analytics.time}s` },
    { icon: Database, label: "Indexed Catalogue", value: `${Number(analytics.catalogueSize || 0).toLocaleString()} Images` },
    { icon: Cpu, label: "AI Model", value: analytics.model },
    { icon: Target, label: "Best Match", value: `${analytics.bestMatch}%` },
    { icon: Calendar, label: "Search Date & Time", value: analytics.timestamp || "—" },
  ];

  const panel = (
    <div className="rounded-3xl border border-gray-200 bg-white/70 backdrop-blur-md shadow-sm shadow-gray-100 p-5 md:p-6 animate-fade-in-up">
      <div className="flex items-center gap-1.5 text-xs font-medium text-blue-700 bg-blue-50 border border-blue-100 rounded-full px-3 py-1 mb-4 w-fit">
        <Sparkles className="w-3.5 h-3.5" /> Search Analytics
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {metrics.map((m) => (
          <div key={m.label} className="rounded-xl border border-gray-200 bg-gray-50/70 px-3.5 py-3">
            <div className="flex items-center gap-1.5 text-gray-500 text-xs mb-1.5">
              <m.icon className="w-3.5 h-3.5" />
              {m.label}
            </div>
            <div className="text-gray-900 text-sm font-semibold truncate">{m.value}</div>
          </div>
        ))}
      </div>
    </div>
  );

  if (tab === "image" && imagePreview) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-[220px_1fr] gap-5 mb-10">
        <div className="rounded-3xl overflow-hidden border border-gray-200 bg-gray-50 animate-fade-in-up">
          <img src={imagePreview} alt="Query" className="w-full h-full max-h-56 md:max-h-full object-cover" />
        </div>
        {panel}
      </div>
    );
  }
  return <div className="mb-10">{panel}</div>;
}

/* ---------------------------------------------------------------------- */
/*  Recent searches                                                         */
/* ---------------------------------------------------------------------- */

function RecentSearches({ items, onSelect }) {
  if (!items.length) return null;
  return (
    <section className="max-w-3xl mx-auto px-5 mt-6 animate-fade-in-up">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">
        <History className="w-3.5 h-3.5" /> Recent Searches
      </div>
      <div className="flex gap-3 overflow-x-auto pb-2 -mx-1 px-1">
        {items.map((s) => (
          <button
            key={s.id}
            onClick={() => onSelect(s)}
            className="flex items-center gap-2.5 flex-shrink-0 rounded-2xl border border-gray-200 bg-white hover:border-blue-200 hover:bg-blue-50/40 transition-colors pl-2 pr-3.5 py-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400"
          >
            {s.thumbnail ? (
              <img src={s.thumbnail} alt="" className="w-9 h-9 rounded-xl object-cover flex-shrink-0" />
            ) : (
              <span className="w-9 h-9 rounded-xl bg-blue-50 flex items-center justify-center flex-shrink-0">
                <Type className="w-4 h-4 text-blue-600" />
              </span>
            )}
            <div className="text-left">
              <div className="text-xs font-semibold text-gray-900">{s.mode}</div>
              <div className="text-[11px] text-gray-400">{s.dateLabel} · {s.timeLabel}</div>
            </div>
            <RotateCcw className="w-3.5 h-3.5 text-gray-300 ml-1 flex-shrink-0" />
          </button>
        ))}
      </div>
    </section>
  );
}

/* ---------------------------------------------------------------------- */
/*  Home page                                                               */
/* ---------------------------------------------------------------------- */

function HomePage({ onViewProduct }) {
  const [tab, setTab] = useState("image");
  const [dragOver, setDragOver] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [query, setQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [recentSearches, setRecentSearches] = useState([]);
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  const examples = ["white floral lace", "black embroidered lace", "stretch mesh fabric", "cotton fabric"];

  function handleFile(file) {
  if (!file) return;

  setSelectedFile(file);

  const reader = new FileReader();

  reader.onload = (e) => {
    setImagePreview(e.target.result);
  };

  reader.readAsDataURL(file);
}
async function runSearch() {
    if (tab === "image" && !selectedFile) return;
    if (tab === "text" && !query.trim()) return;

    setIsSearching(true);
    setResults(null);
    setAnalytics(null);

    const startTime = performance.now();

    try {
      // ================================================================
      // TEXT SEARCH
      // ================================================================
      if (tab === "text") {
        const response = await fetch(
          `http://127.0.0.1:8000/api/text-search?q=${encodeURIComponent(query.trim())}&top_k=10`
        );

        if (!response.ok) {
          throw new Error(`Text search failed: ${response.status}`);
        }

        const data = await response.json();

        if (!data.success) {
          throw new Error(data.message || "Text search was unsuccessful.");
        }

        const rawResults = Array.isArray(data.results) ? data.results : [];

        const backendResults = rawResults.map((item, index) => {
          const rawPath = String(item.image || "").replace(/\\/g, "/");
          const imageUrl = rawPath
            ? (rawPath.startsWith("http://") || rawPath.startsWith("https://")
                ? rawPath
                : `http://127.0.0.1:8000${rawPath.startsWith("/") ? "" : "/"}${rawPath}`)
            : "";

          const productId = item.product_id || `RESULT-${index + 1}`;

          return {
            id: `${productId}-${index}`,
            sku: productId,
            name: item.name || productId,
            category: item.category || "Lace",
            material: item.material || "—",
            pattern: item.pattern || "—",
            width: item.width || "—",
            gsm: item.gsm || "—",
            description: item.description || "Catalogue product.",
            applications:
              Array.isArray(item.applications) && item.applications.length
                ? item.applications
                : [],
            similarity: undefined,
            imageUrl,
          };
        });

        setResults(backendResults);

        const searchTime = ((performance.now() - startTime) / 1000).toFixed(2);

        setAnalytics({
          mode: "Text Search",
          time: searchTime,
          catalogueSize: data.catalogue_size ?? data.total_products ?? 74,
          model: "Catalogue Metadata Search",
          bestMatch: backendResults.length ? "Matched" : "—",
          timestamp: new Date().toLocaleString([], { dateStyle: "short", timeStyle: "short" }),
        });

        return;
      }

      // ================================================================
      // IMAGE SEARCH
      // ================================================================
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch("http://127.0.0.1:8000/api/search", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Image search failed: ${response.status}`);
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.message || "Backend search was unsuccessful.");
      }

      const rawResults = Array.isArray(data.results) ? data.results : [];

      const backendResults = rawResults.map((item, index) => {
        const rawPath = String(item.image || "").replace(/\\/g, "/");
        const imageUrl = rawPath
          ? (rawPath.startsWith("http://") || rawPath.startsWith("https://")
              ? rawPath
              : `http://127.0.0.1:8000${rawPath.startsWith("/") ? "" : "/"}${rawPath}`)
          : "";

        const productId = item.product_id || `RESULT-${index + 1}`;
        const rawScore = Number(item.score ?? 0);
        const similarity = rawScore <= 1
          ? (rawScore * 100).toFixed(1)
          : Math.min(rawScore, 100).toFixed(1);

        return {
          id: `${productId}-${index}`,
          sku: productId,
          name: item.name || productId,
          category: item.category || "Lace",
          material: item.material || "—",
          pattern: item.pattern || "—",
          width: item.width || "—",
          gsm: item.gsm || "—",
          description: item.description || "AI visual match from the lace catalogue.",
          applications:
            Array.isArray(item.applications) && item.applications.length
              ? item.applications
              : ["Visual Search"],
          similarity,
          imageUrl,
        };
      });

      setResults(backendResults);

      const searchTime = ((performance.now() - startTime) / 1000).toFixed(2);

      setAnalytics({
        mode: "Image Search",
        time: searchTime,
        catalogueSize: data.catalogue_size ?? data.index_size ?? data.total_images ?? 89,
        model: data.model || "Marqo FashionSigLIP",
        bestMatch: backendResults[0]?.similarity || "0.0",
        timestamp: new Date().toLocaleString([], { dateStyle: "short", timeStyle: "short" }),
      });
    } catch (error) {
      console.error("Search error:", error);
      alert(`Search error: ${error.message}`);
    } finally {
      setIsSearching(false);
    }
  }

  function restoreSearch(s) {
    setTab(s.tab);
    if (s.tab === "image") setImagePreview(s.image);
    else setQuery(s.query);
    setTimeout(runSearch, 0);
  }

  return (
    <div>
      {/* Hero */}
      <section className="max-w-4xl mx-auto text-center px-5 pt-16 md:pt-24 pb-12 animate-fade-in">
        <div className="inline-flex items-center gap-1.5 text-xs font-medium text-blue-700 bg-blue-50 border border-blue-100 rounded-full px-3 py-1.5 mb-7">
          <Sparkles className="w-3.5 h-3.5" /> AI-Powered Visual Matching
        </div>
        <h1
          className="text-4xl sm:text-5xl md:text-6xl font-semibold tracking-tight mb-6 leading-[1.08]"
          style={{
            ...fontDisplay,
            color: "#111827",
          }}
        >
          AI Fabric &amp; Lace<br className="hidden sm:block" /> Visual Search
        </h1>
        <p className="text-base md:text-lg text-gray-500 max-w-2xl mx-auto leading-relaxed">
          Find visually similar lace and fabric samples instantly using advanced AI-powered visual and text search.
        </p>
      </section>

      {/* Search card */}
      <section className="max-w-3xl mx-auto px-5">
        <div className="rounded-3xl border border-gray-200 bg-white shadow-sm shadow-gray-100 p-2 animate-fade-in-up">
          <div className="flex gap-1 p-1.5">
            {[
              { key: "image", label: "Image Search", icon: ImageIcon },
              { key: "text", label: "Text Search", icon: Type },
            ].map((t) => (
              <button
                key={t.key}
                onClick={() => {
                  setTab(t.key);
                  setImagePreview(null);
                  setSelectedFile(null);
                  setQuery("");
                  setResults(null);
                  setAnalytics(null);
                }}
                className={`flex-1 flex items-center justify-center gap-2 text-sm font-medium py-3 rounded-2xl transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 ${
                  tab === t.key ? "bg-blue-600 text-white shadow-sm" : "text-gray-500 hover:bg-gray-50"
                }`}
              >
                <t.icon className="w-4 h-4" /> {t.label}
              </button>
            ))}
          </div>

          <div className="p-5 pt-3">
            {tab === "image" ? (
              <div>
                {!imagePreview ? (
                  <div
                    onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                    onDragLeave={() => setDragOver(false)}
                    onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files?.[0]); }}
                    className={`rounded-2xl border-2 border-dashed transition-colors duration-200 flex flex-col items-center justify-center text-center py-16 px-6 ${
                      dragOver ? "border-blue-400 bg-blue-50/60" : "border-gray-200 bg-gray-50/60"
                    }`}
                  >
                    <div className="w-14 h-14 rounded-2xl bg-white border border-gray-200 flex items-center justify-center mb-4 shadow-sm">
                      <Upload className="w-6 h-6 text-blue-600" />
                    </div>
                    <p className="text-sm font-medium text-gray-900 mb-1">Drag &amp; drop an image here</p>
                    <p className="text-xs text-gray-500 mb-6">PNG, JPG up to 10MB</p>
                    <div className="flex items-center gap-3">
                      <Btn variant="secondary" size="md" icon={Upload} onClick={() => fileInputRef.current?.click()}>Upload Image</Btn>
                      <Btn variant="secondary" size="md" icon={Camera} onClick={() => cameraInputRef.current?.click()}>Use Camera</Btn>
                    </div>
                    <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={(e) => handleFile(e.target.files?.[0])} />
                    <input ref={cameraInputRef} type="file" accept="image/*" capture="environment" className="hidden" onChange={(e) => handleFile(e.target.files?.[0])} />
                  </div>
                ) : (
                  <div className="relative rounded-2xl overflow-hidden border border-gray-200">
                    <img src={imagePreview} alt="Uploaded preview" className="w-full max-h-80 object-contain bg-gray-50" />
                    <button
                      onClick={() => {
                        setImagePreview(null);
                        setSelectedFile(null);
                        setResults(null);
                        setAnalytics(null);
                      }}
                      className="absolute top-3 right-3 w-8 h-8 rounded-full bg-white/90 border border-gray-200 flex items-center justify-center hover:bg-white focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400"
                    >
                      <X className="w-4 h-4 text-gray-700" />
                    </button>
                  </div>
                )}
                <Btn className="mt-4 w-full" size="lg" variant="primary" disabled={!selectedFile} loading={isSearching} icon={Search} onClick={runSearch}>
                  {isSearching ? "Searching…" : "Search"}
                </Btn>
              </div>
            ) : (
              <div>
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && runSearch()}
                    placeholder="Search by describing a lace or fabric…"
                    className="w-full pl-11 pr-4 py-4 rounded-2xl border border-gray-200 bg-gray-50/60 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-300 transition-all"
                  />
                </div>
                <div className="flex flex-wrap gap-2 mt-3">
                  {examples.map((ex) => (
                    <button
                      key={ex}
                      onClick={() => setQuery(ex)}
                      className="text-xs font-medium px-3 py-1.5 rounded-full bg-gray-50 border border-gray-200 text-gray-500 hover:text-blue-600 hover:border-blue-200 hover:bg-blue-50 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400"
                    >
                      {ex}
                    </button>
                  ))}
                </div>
                <Btn className="mt-4 w-full" size="lg" variant="primary" disabled={!query.trim()} loading={isSearching} icon={Search} onClick={runSearch}>
                  {isSearching ? "Searching…" : "Search"}
                </Btn>
              </div>
            )}
          </div>
        </div>
      </section>

      <RecentSearches items={recentSearches} onSelect={restoreSearch} />

      {/* Feature strip */}
      {!results && !isSearching && (
        <section className="max-w-5xl mx-auto px-5 mt-16 grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { icon: Zap, title: "Instant matching", desc: "Sub-second visual similarity across the full catalogue." },
            { icon: ShieldCheck, title: "Spec-accurate", desc: "Material, GSM and width verified for every result." },
            { icon: Gauge, title: "Production ready", desc: "Built for sourcing teams at scale." },
          ].map((f) => (
            <div key={f.title} className="rounded-2xl border border-gray-200 bg-gray-50/60 p-5">
              <f.icon className="w-5 h-5 text-blue-600 mb-3" />
              <div className="text-sm font-semibold text-gray-900 mb-1">{f.title}</div>
              <div className="text-xs text-gray-500 leading-relaxed">{f.desc}</div>
            </div>
          ))}
        </section>
      )}

      {/* Results */}
      <section className="max-w-6xl mx-auto px-5 mt-14 pb-24">
        {isSearching && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900" style={fontDisplay}>Searching catalogue…</h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
              {Array.from({ length: 8 }).map((_, i) => <SkeletonCard key={i} />)}
            </div>
          </div>
        )}
        {results && !isSearching && (
          <div>
            {analytics && <SearchAnalyticsPanel analytics={analytics} imagePreview={imagePreview} tab={tab} />}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900" style={fontDisplay}>{results.length} Results</h2>
              <span className="text-xs text-gray-400">Sorted by similarity</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
              {results.map((p, i) => (
                <ResultCard key={p.id} product={p} onView={() => onViewProduct(p, "search")} style={{ animationDelay: `${i * 40}ms` }} />
              ))}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

/* ---------------------------------------------------------------------- */
/*  Catalogue page                                                          */
/* ---------------------------------------------------------------------- */

function CataloguePage({ onViewProduct, goTo, products, loading, error }) {
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState([]);

  const toggleFilter = (cat) =>
    setFilters((f) =>
      f.includes(cat) ? f.filter((c) => c !== cat) : [...f, cat]
    );

  const filtered = products.filter((p) => {
    const matchesFilter =
      filters.length === 0 || filters.includes(p.category);
    const q = query.trim().toLowerCase();
    const matchesQuery =
      !q ||
      [p.sku, p.name, p.description, p.material, p.pattern, p.category]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(q);
    return matchesFilter && matchesQuery;
  });

  return (
    <div className="max-w-4xl mx-auto px-5 pt-8 pb-24 animate-fade-in">
      <div className="flex items-center gap-1.5 text-xs text-gray-400 mb-5">
        <button onClick={() => goTo("home")} className="hover:text-gray-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 rounded">Home</button>
        <ChevronRight className="w-3 h-3" />
        <span className="text-gray-600 font-medium">Catalogue</span>
      </div>

      <div className="flex items-end justify-between gap-4 mb-7">
        <div>
          <h1 className="text-3xl font-semibold text-gray-900 tracking-tight" style={fontDisplay}>Browse Catalogue</h1>
          <p className="text-xs text-gray-400 mt-1">{loading ? "Loading catalogue…" : `${products.length} catalogue products`}</p>
        </div>
      </div>

      <div className="sticky top-16 z-30 bg-white/90 backdrop-blur-md pt-1 pb-4 -mx-5 px-5">
        <div className="relative mb-4">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search catalogue by SKU, name or description…"
            className="w-full pl-11 pr-4 py-3.5 rounded-2xl border border-gray-200 bg-gray-50/60 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-300 transition-all"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <span className="flex items-center gap-1.5 text-xs text-gray-400 mr-1">
            <SlidersHorizontal className="w-3.5 h-3.5" /> Filter
          </span>
          {Object.keys(CATEGORY_META).map((cat) => {
            const active = filters.includes(cat);
            const count = products.filter((p) => p.category === cat).length;
            if (count === 0) return null;
            return (
              <button
                key={cat}
                onClick={() => toggleFilter(cat)}
                className={`inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full border transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 ${
                  active ? "bg-blue-50 border-blue-200 text-blue-700" : "bg-white border-gray-200 text-gray-600 hover:bg-gray-50"
                }`}
              >
                <CategoryDot category={cat} /> {CATEGORY_META[cat].label}
                <span className="text-gray-400">{count}</span>
                {active && <Check className="w-3 h-3" />}
              </button>
            );
          })}
        </div>
      </div>

      {error && (
        <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 mb-3">
          Could not load the catalogue from the backend: {error}
        </div>
      )}

      <div className="rounded-2xl border border-gray-200 overflow-hidden bg-white mt-2">
        {loading && (
          <div className="py-16 text-center text-sm text-gray-400">Loading your catalogue…</div>
        )}
        {!loading && filtered.length === 0 && (
          <div className="py-16 text-center text-sm text-gray-400">No items match your search.</div>
        )}
        {!loading && filtered.map((p, i) => (
          <button
            key={p.id}
            onClick={() => onViewProduct(p, "catalogue")}
            className={`group w-full flex items-center gap-3 px-5 py-4 text-left hover:bg-gray-50 transition-colors duration-150 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 focus-visible:ring-inset min-h-[44px] ${
              i !== 0 ? "border-t border-gray-100" : ""
            }`}
          >
            <CategoryDot category={p.category} />
            <span className="text-xs font-medium text-gray-400 w-24 flex-shrink-0">{p.sku}</span>
            <span className="text-sm text-gray-900 font-medium flex-1 truncate group-hover:text-blue-700 transition-colors">{p.name}</span>
            <ChevronRight className="w-4 h-4 text-gray-300 flex-shrink-0 transition-transform duration-150 group-hover:translate-x-0.5 group-hover:text-blue-500" />
          </button>
        ))}
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------------- */
/*  Related products carousel                                              */
/* ---------------------------------------------------------------------- */

function RelatedCarousel({ products, onView }) {
  const scrollerRef = useRef(null);
  const scrollBy = (dx) => scrollerRef.current?.scrollBy({ left: dx, behavior: "smooth" });

  return (
    <div className="relative">
      <div className="flex items-center justify-end gap-2 mb-3">
        <button onClick={() => scrollBy(-320)} className="w-8 h-8 rounded-full border border-gray-200 flex items-center justify-center hover:bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400" aria-label="Scroll left">
          <ChevronLeft className="w-4 h-4 text-gray-600" />
        </button>
        <button onClick={() => scrollBy(320)} className="w-8 h-8 rounded-full border border-gray-200 flex items-center justify-center hover:bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400" aria-label="Scroll right">
          <ChevronRight className="w-4 h-4 text-gray-600" />
        </button>
      </div>
      <div ref={scrollerRef} className="flex gap-5 overflow-x-auto pb-2 snap-x snap-mandatory scroll-smooth">
        {products.map((p, i) => (
          <div key={p.id} className="w-[260px] flex-shrink-0 snap-start">
            <ResultCard product={p} onView={() => onView(p)} style={{ animationDelay: `${i * 40}ms` }} />
          </div>
        ))}
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------------- */
/*  Product details page                                                    */
/* ---------------------------------------------------------------------- */

function ProductDetailsPage({ product, source, goTo, onViewProduct, catalogueProducts }) {
  const similar = useMemo(() => {
    const pool = catalogueProducts?.length ? catalogueProducts : [];
    const others = pool.filter((p) => p.category === product.category && p.id !== product.id);
    const rand = mulberry32(seedFromString(product.sku + "similar"));
    return [...others].sort(() => rand() - 0.5).slice(0, 6).map((p) => ({ ...p, similarity: (75 + rand() * 22).toFixed(1) }));
  }, [product]);

  const simColor = product.similarity != null ? similarityColor(product.similarity) : null;

  return (
    <div className="max-w-5xl mx-auto px-5 pt-8 pb-28 md:pb-24 animate-fade-in">
      <div className="flex items-center gap-1.5 text-xs text-gray-400 mb-6 flex-wrap">
        <button onClick={() => goTo("home")} className="hover:text-gray-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 rounded">Home</button>
        <ChevronRight className="w-3 h-3" />
        {source === "catalogue" ? (
          <button onClick={() => goTo("catalogue")} className="hover:text-gray-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 rounded">Catalogue</button>
        ) : (
          <span>Search Results</span>
        )}
        <ChevronRight className="w-3 h-3" />
        <span className="text-gray-600 font-medium truncate max-w-[200px]">{product.name}</span>
      </div>

      <button
        onClick={() => goTo(source === "catalogue" ? "catalogue" : "home")}
        className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-500 hover:text-gray-900 mb-6 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 rounded"
      >
        <ArrowLeft className="w-3.5 h-3.5" /> Back
      </button>

      <div className="grid md:grid-cols-2 gap-9">
        <div className="rounded-3xl overflow-hidden border border-gray-200 shadow-sm">
          <Swatch product={product} className="w-full aspect-square" />
        </div>

        <div>
          <div className="flex items-center gap-2 mb-3">
            <CategoryDot category={product.category} />
            <span className="text-xs font-medium text-gray-400">{product.sku}</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-semibold text-gray-900 mb-4 leading-snug tracking-tight" style={fontDisplay}>
            {product.name}
          </h1>

          {product.similarity != null && (
            <div className={`flex items-center gap-4 mb-5 p-4 rounded-2xl border ${simColor.bg} ${simColor.border}`}>
              <div className="text-3xl font-semibold tracking-tight" style={{ ...fontDisplay, color: simColor.bar }}>
                {product.similarity}%
              </div>
              <div>
                <div className="text-xs font-semibold text-gray-900">AI Similarity Score</div>
                <div className="w-32 mt-1.5"><SimilarityBar value={product.similarity} /></div>
              </div>
            </div>
          )}

          <div className="flex items-start gap-2 mb-6 p-4 rounded-2xl bg-blue-50/60 border border-blue-100">
            <Sparkles className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-blue-900 leading-relaxed">{product.description}</p>
          </div>

          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Specifications</h3>
          <SpecTable product={product} />

          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3 mt-6">Recommended Applications</h3>
          <div className="flex flex-wrap gap-2 mb-8">
            {(product.applications || []).map((a) => (
              <span key={a} className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full bg-gray-50 border border-gray-200 text-gray-600">
                <CheckCircle2 className="w-3.5 h-3.5 text-gray-400" /> {a}
              </span>
            ))}
          </div>

          <div className="hidden md:grid grid-cols-2 gap-3">
            <Btn variant="primary" size="lg" icon={Download}>Download Spec</Btn>
            <Btn variant="secondary" size="lg" icon={ScanSearch}>Find Similar</Btn>
          </div>
        </div>
      </div>

      <div className="mt-20">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900 tracking-tight" style={fontDisplay}>Similar Products</h2>
          <span className="hidden sm:inline-flex items-center gap-1 text-xs text-gray-400"><ArrowUpRight className="w-3.5 h-3.5" /> AI-ranked</span>
        </div>
        <RelatedCarousel products={similar} onView={(p) => onViewProduct(p, source)} />
      </div>

      {/* sticky mobile action bar */}
      <div className="md:hidden fixed bottom-16 inset-x-0 z-30 bg-white/95 backdrop-blur-md border-t border-gray-200 px-4 py-3 flex gap-3">
        <Btn variant="primary" size="md" icon={Download} className="flex-1">Download Spec</Btn>
        <Btn variant="secondary" size="md" icon={ScanSearch} className="flex-1">Find Similar</Btn>
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------------- */
/*  About page                                                              */
/* ---------------------------------------------------------------------- */

function AboutPage({ goTo }) {
  const stats = [
    { value: "89", label: "Catalogue images indexed" },
    { value: "74", label: "Catalogue products" },
    { value: "Top-5", label: "Visual matches returned" },
  ];
  const steps = [
    { icon: Upload, title: "Upload or describe", desc: "Provide a photo, sketch or text description of the fabric or lace you're sourcing." },
    { icon: ScanSearch, title: "AI visual matching", desc: "Our model compares texture, pattern and colour against the full catalogue." },
    { icon: Eye, title: "Review ranked results", desc: "Browse matches ranked by similarity, complete with verified specifications." },
  ];
  return (
    <div className="max-w-3xl mx-auto px-5 pt-8 pb-24 animate-fade-in">
      <div className="flex items-center gap-1.5 text-xs text-gray-400 mb-6">
        <button onClick={() => goTo("home")} className="hover:text-gray-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 rounded">Home</button>
        <ChevronRight className="w-3 h-3" />
        <span className="text-gray-600 font-medium">About</span>
      </div>

      <h1 className="text-3xl font-semibold text-gray-900 mb-4 tracking-tight" style={fontDisplay}>Built for textile sourcing teams</h1>
      <p className="text-sm md:text-base text-gray-500 leading-relaxed mb-10">
        AI Fabric &amp; Lace Visual Search helps manufacturers, designers and sourcing teams locate the closest
        matching lace and fabric samples in seconds, using AI-powered image and text comparison across a
        continuously growing catalogue.
      </p>

      <div className="grid grid-cols-3 gap-3 mb-12">
        {stats.map((s) => (
          <div key={s.label} className="rounded-2xl border border-gray-200 bg-gray-50/60 p-4 text-center">
            <div className="text-xl md:text-2xl font-semibold text-blue-600 mb-1 tracking-tight" style={fontDisplay}>{s.value}</div>
            <div className="text-[11px] text-gray-500 leading-snug">{s.label}</div>
          </div>
        ))}
      </div>

      <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-4">How it works</h2>
      <div className="space-y-3 mb-4">
        {steps.map((s) => (
          <div key={s.title} className="flex items-start gap-4 rounded-2xl border border-gray-200 p-4">
            <div className="w-9 h-9 rounded-xl bg-blue-50 flex items-center justify-center flex-shrink-0">
              <s.icon className="w-4 h-4 text-blue-600" />
            </div>
            <div>
              <div className="text-sm font-semibold text-gray-900 mb-0.5">{s.title}</div>
              <div className="text-xs text-gray-500 leading-relaxed">{s.desc}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------------- */
/*  Root App                                                                */
/* ---------------------------------------------------------------------- */

export default function App() {
  const [page, setPage] = useState("home");
  const [mobileOpen, setMobileOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [source, setSource] = useState("catalogue");
  const [catalogueProducts, setCatalogueProducts] = useState([]);
  const [catalogueLoading, setCatalogueLoading] = useState(true);
  const [catalogueError, setCatalogueError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadCatalogue() {
      try {
        setCatalogueLoading(true);
        setCatalogueError("");
        const response = await fetch(`${API_BASE_URL}/api/catalogue`);
        if (!response.ok) throw new Error(`Catalogue request failed: ${response.status}`);
        const data = await response.json();
        if (!data.success) throw new Error(data.message || "Catalogue request was unsuccessful.");
        const items = Array.isArray(data.products) ? data.products : [];
        if (!cancelled) {
          setCatalogueProducts(items.map(normalizeCatalogueProduct));
        }
      } catch (err) {
        if (!cancelled) setCatalogueError(err.message || "Unable to load catalogue.");
      } finally {
        if (!cancelled) setCatalogueLoading(false);
      }
    }

    loadCatalogue();
    return () => { cancelled = true; };
  }, []);

  function goTo(p) {
    setPage(p);
    setMobileOpen(false);
    window.scrollTo?.({ top: 0, behavior: "smooth" });
  }

  function viewProduct(product, src) {
    setSelectedProduct(product);
    setSource(src);
    setPage("product");
    window.scrollTo?.({ top: 0, behavior: "smooth" });
  }

  return (
    <div className="min-h-screen bg-white antialiased" style={fontBody}>
      <FontLoader />
      <style>{`
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes ripple { from { transform: scale(0); opacity: 0.55; } to { transform: scale(1); opacity: 0; } }
        @keyframes shimmer { 0% { background-position: -400px 0; } 100% { background-position: 400px 0; } }
        .animate-fade-in { animation: fadeIn 0.5s ease-out both; }
        .animate-fade-in-up { animation: fadeInUp 0.6s ease-out both; }
        .animate-ripple { animation: ripple 0.6s ease-out forwards; }
        .afl-shimmer { background: linear-gradient(90deg, #f3f4f6 25%, #eef0f3 37%, #f3f4f6 63%); background-size: 800px 100%; animation: shimmer 1.4s ease-in-out infinite; }
        .line-clamp-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        * { -webkit-tap-highlight-color: transparent; }
      `}</style>

      <Navbar page={page} goTo={goTo} mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} />

      <main className="pb-16 md:pb-0">
        {page === "home" && <HomePage onViewProduct={viewProduct} />}
        {page === "catalogue" && (
          <CataloguePage
            onViewProduct={viewProduct}
            goTo={goTo}
            products={catalogueProducts}
            loading={catalogueLoading}
            error={catalogueError}
          />
        )}
        {page === "about" && <AboutPage goTo={goTo} />}
        {page === "product" && selectedProduct && (
          <ProductDetailsPage
            product={selectedProduct}
            source={source}
            goTo={goTo}
            onViewProduct={viewProduct}
            catalogueProducts={catalogueProducts}
          />
        )}
      </main>

      <BottomNav page={page === "product" ? source : page} goTo={goTo} />
    </div>
  );
}