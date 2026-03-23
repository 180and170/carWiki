(() => {
  "use strict";

  const DATA_BASE = "data";

  let catalogData = null;
  let allProducts = [];
  let displayedProducts = 0;
  const PAGE_SIZE = 24;

  // ── Initialization ──

  async function init() {
    try {
      const resp = await fetch(`${DATA_BASE}/catalog.json`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      catalogData = await resp.json();
    } catch (err) {
      console.error("Failed to load catalog data:", err);
      document.getElementById("brands-grid").innerHTML =
        '<div class="loading">数据加载失败，请稍后刷新重试。</div>';
      return;
    }

    const meta = catalogData.meta || {};
    document.getElementById("brand-count").textContent = meta.total_brands || 0;
    document.getElementById("product-count").textContent = meta.total_products || 0;

    if (meta.last_updated) {
      const d = new Date(meta.last_updated);
      document.getElementById("last-updated").textContent = d.toLocaleString("zh-CN");
    }

    flattenProducts();
    renderBrands();
    populateBrandSelect();
    setupNavigation();
    setupFilters();
    setupSearch();
    setupModal();
    renderAboutBrands();
  }

  function flattenProducts() {
    allProducts = [];
    const products = catalogData.products || {};
    for (const [brandKey, items] of Object.entries(products)) {
      for (const item of items) {
        allProducts.push({ ...item, brandKey });
      }
    }
  }

  // ── Navigation ──

  function setupNavigation() {
    document.querySelectorAll(".nav-link").forEach(link => {
      link.addEventListener("click", e => {
        e.preventDefault();
        const section = link.dataset.section;
        showSection(section);
        document.querySelectorAll(".nav-link").forEach(l => l.classList.remove("active"));
        link.classList.add("active");
      });
    });
  }

  function showSection(name) {
    ["brands", "products", "about"].forEach(s => {
      const el = document.getElementById(s);
      if (el) el.style.display = s === name ? "block" : "none";
    });
    if (name === "products" && displayedProducts === 0) {
      renderProducts();
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // ── Brands ──

  const REGION_MAP = {
    "中国香港": "中国香港",
    "美国": "美国",
    "美国/中国香港": "美国",
    "日本": "日本",
    "英国/美国": "欧洲",
    "法国/泰国": "欧洲",
    "德国": "欧洲",
  };

  function renderBrands(regionFilter = "all") {
    const brands = catalogData.brands || {};
    const grid = document.getElementById("brands-grid");
    grid.innerHTML = "";

    const entries = Object.entries(brands);
    let count = 0;

    for (const [key, brand] of entries) {
      const region = REGION_MAP[brand.country] || brand.country;
      if (regionFilter !== "all" && region !== regionFilter) continue;
      count++;

      const products = (catalogData.products || {})[key] || [];
      const card = document.createElement("div");
      card.className = "brand-card";
      card.dataset.key = key;

      card.innerHTML = `
        <div class="brand-card-header">
          <div class="brand-name">${esc(brand.name)}</div>
          <div class="brand-country">${esc(brand.country)}</div>
        </div>
        <div class="brand-desc">${esc(brand.description)}</div>
        <div class="brand-meta">
          <div class="brand-meta-item">&#128197; 创立于 ${esc(brand.founded)}</div>
          <div class="brand-meta-item">&#128230; ${products.length} 款产品</div>
        </div>
        <div class="brand-tags">
          ${(brand.specialty || []).map(s => `<span class="tag">${esc(s)}</span>`).join("")}
        </div>
      `;

      card.addEventListener("click", () => showBrandModal(key));
      grid.appendChild(card);
    }

    if (count === 0) {
      grid.innerHTML = '<div class="loading">该地区暂无品牌数据</div>';
    }
  }

  function setupFilters() {
    document.querySelectorAll(".filter-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        renderBrands(btn.dataset.region);
      });
    });
  }

  // ── Brand Modal ──

  function setupModal() {
    const modal = document.getElementById("brand-modal");
    modal.querySelector(".modal-overlay").addEventListener("click", closeModal);
    modal.querySelector(".modal-close").addEventListener("click", closeModal);
    document.addEventListener("keydown", e => {
      if (e.key === "Escape") closeModal();
    });
  }

  function closeModal() {
    document.getElementById("brand-modal").style.display = "none";
    document.body.style.overflow = "";
  }

  function showBrandModal(brandKey) {
    const brand = catalogData.brands[brandKey];
    if (!brand) return;

    const products = (catalogData.products || {})[brandKey] || [];
    const body = document.getElementById("modal-body");

    body.innerHTML = `
      <div class="modal-brand-name">${esc(brand.name)}</div>
      <div class="modal-brand-full">${esc(brand.full_name)}</div>
      <div class="modal-info">
        <div class="modal-info-item">
          <label>国家/地区</label>
          <span>${esc(brand.country)}</span>
        </div>
        <div class="modal-info-item">
          <label>创立年份</label>
          <span>${esc(brand.founded)}</span>
        </div>
        <div class="modal-info-item">
          <label>比例</label>
          <span>1/64</span>
        </div>
        <div class="modal-info-item">
          <label>已收录产品</label>
          <span>${products.length} 款</span>
        </div>
      </div>
      <div class="modal-desc">${esc(brand.description)}</div>
      <div class="modal-specialties">
        ${(brand.specialty || []).map(s => `<span class="tag">${esc(s)}</span>`).join("")}
      </div>
      <a href="${esc(brand.website)}" target="_blank" rel="noopener" class="modal-link">
        访问官网 &rarr;
      </a>
      ${products.length > 0 ? `
        <div class="modal-products-title">产品数据</div>
        <div class="modal-product-count">已收录 ${products.length} 款产品</div>
        <button class="view-products-btn" data-brand="${esc(brandKey)}">
          查看该品牌产品 &rarr;
        </button>
      ` : ""}
    `;

    const vpBtn = body.querySelector(".view-products-btn");
    if (vpBtn) {
      vpBtn.addEventListener("click", () => {
        closeModal();
        document.getElementById("brand-select").value = brandKey;
        showSection("products");
        document.querySelectorAll(".nav-link").forEach(l => l.classList.remove("active"));
        document.querySelector('[data-section="products"]').classList.add("active");
        renderProducts();
      });
    }

    document.getElementById("brand-modal").style.display = "flex";
    document.body.style.overflow = "hidden";
  }

  // ── Products ──

  function populateBrandSelect() {
    const select = document.getElementById("brand-select");
    const brands = catalogData.brands || {};
    for (const [key, brand] of Object.entries(brands)) {
      const opt = document.createElement("option");
      opt.value = key;
      opt.textContent = brand.name;
      select.appendChild(opt);
    }
    select.addEventListener("change", () => {
      displayedProducts = 0;
      renderProducts();
    });
  }

  function setupSearch() {
    let timer;
    document.getElementById("search-input").addEventListener("input", () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        displayedProducts = 0;
        renderProducts();
      }, 300);
    });

    document.getElementById("load-more-btn").addEventListener("click", () => {
      renderProducts(true);
    });
  }

  function getFilteredProducts() {
    const brandKey = document.getElementById("brand-select").value;
    const query = document.getElementById("search-input").value.trim().toLowerCase();

    let filtered = allProducts;

    if (brandKey !== "all") {
      filtered = filtered.filter(p => p.brandKey === brandKey);
    }

    if (query) {
      filtered = filtered.filter(p =>
        (p.name || "").toLowerCase().includes(query) ||
        (p.brand || "").toLowerCase().includes(query) ||
        (p.sku || "").toLowerCase().includes(query)
      );
    }

    return filtered;
  }

  function renderProducts(append = false) {
    const grid = document.getElementById("products-grid");
    const noResults = document.getElementById("no-results");
    const loadMoreWrap = document.getElementById("load-more-wrap");

    if (!append) {
      grid.innerHTML = "";
      displayedProducts = 0;
    }

    const filtered = getFilteredProducts();

    if (filtered.length === 0) {
      grid.innerHTML = "";
      noResults.style.display = "block";
      loadMoreWrap.style.display = "none";
      return;
    }

    noResults.style.display = "none";

    const slice = filtered.slice(displayedProducts, displayedProducts + PAGE_SIZE);

    for (const product of slice) {
      const card = document.createElement("div");
      card.className = "product-card";

      const hasImage = product.image && !product.image.includes("icon") && !product.image.includes("logo") && !product.image.includes(".svg");

      card.innerHTML = `
        ${hasImage
          ? `<img class="product-card-img" src="${esc(product.image)}" alt="${esc(product.name)}" loading="lazy" onerror="this.parentElement.querySelector('.product-card-img')?.replaceWith(createPlaceholder())">`
          : `<div class="product-card-img-placeholder">&#128663;</div>`
        }
        <div class="product-card-body">
          <div class="product-card-brand">${esc(product.brand)}</div>
          <div class="product-card-name">${esc(product.name)}</div>
          <div class="product-card-footer">
            <span class="product-card-price">${esc(product.price || "")}</span>
            <span class="product-card-scale">${esc(product.scale || "1/64")}</span>
          </div>
          ${product.url ? `<a href="${esc(product.url)}" target="_blank" rel="noopener" class="product-card-link">查看详情 &rarr;</a>` : ""}
        </div>
      `;

      const img = card.querySelector(".product-card-img");
      if (img) {
        img.addEventListener("error", function () {
          const ph = document.createElement("div");
          ph.className = "product-card-img-placeholder";
          ph.innerHTML = "&#128663;";
          this.replaceWith(ph);
        });
      }

      grid.appendChild(card);
    }

    displayedProducts += slice.length;

    if (displayedProducts < filtered.length) {
      loadMoreWrap.style.display = "block";
    } else {
      loadMoreWrap.style.display = "none";
    }
  }

  // ── About ──

  function renderAboutBrands() {
    const container = document.getElementById("about-brand-list");
    const brands = catalogData.brands || {};
    container.innerHTML = Object.values(brands)
      .map(b => `<span class="tag">${esc(b.name)} (${esc(b.country)})</span>`)
      .join("");
  }

  // ── Helpers ──

  function esc(str) {
    if (!str) return "";
    const el = document.createElement("span");
    el.textContent = str;
    return el.innerHTML;
  }

  // ── Start ──
  document.addEventListener("DOMContentLoaded", init);
})();
