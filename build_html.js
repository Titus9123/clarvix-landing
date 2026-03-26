const fs = require('fs');
const cheerio = require('cheerio');
const i18n = require('./i18n.js');

const HTML_FILE = 'template.html';

// 1. Read the template HTML source
const htmlSource = fs.readFileSync(HTML_FILE, 'utf8');

function processHtml(lang) {
  const $ = cheerio.load(htmlSource, { decodeEntities: false });

  // Set the <html> lang attribute
  $('html').attr('lang', lang);
  if (lang === 'he') {
    $('html').attr('dir', 'rtl');
  }

  // Handle Translations
  if (lang !== 'en') {
    function traverseTranslate(node) {
      if (node.type === 'tag' && node.name !== 'script' && node.name !== 'style') {
        if (node.attribs && node.attribs.placeholder) {
          const key = node.attribs.placeholder.trim();
          if (i18n[key] && i18n[key][lang]) {
            node.attribs.placeholder = i18n[key][lang];
          }
        }
      }
      if (node.type === 'text') {
        const key = node.data.trim();
        if (key && i18n[key] && i18n[key][lang]) {
          node.data = node.data.replace(key, i18n[key][lang]);
        }
      }
      const children = node.children || [];
      for (let i = 0; i < children.length; i++) {
        traverseTranslate(children[i]);
      }
    }
    traverseTranslate($('body')[0]);
  }

  // Replace the old language toggle buttons
  const langToggle = $('.lang-toggle');
  if (langToggle.length) {
    langToggle.html(`
      <a href="index.html" class="lang-btn ${lang === 'en' ? 'active' : ''}" style="text-decoration:none">EN</a><span class="lang-sep">|</span>
      <a href="es.html" class="lang-btn ${lang === 'es' ? 'active' : ''}" style="text-decoration:none">ES</a><span class="lang-sep">|</span>
      <a href="he.html" class="lang-btn ${lang === 'he' ? 'active' : ''}" style="text-decoration:none">HE</a>
    `);
  }

  // Handle the videos
  $('style').each((_, el) => {
    const $style = $(el);
    if ($style.html().includes('html[lang="es"]')) {
      $style.remove();
    }
  });

  const videoWrapper = $('.video-wrapper');
  if (videoWrapper.length) {
    if (lang === 'en') {
      videoWrapper.find('.video-es').remove();
    } else if (lang === 'es') {
      videoWrapper.find('.video-en').remove();
    } else if (lang === 'he') {
      // Hebrew fallback to English video
      videoWrapper.find('.video-es').remove();
    }
  }

  // SEO Metadata Injection
  let siteTitle = "Clarvix — Lead Conversion Digital Audit";
  let siteDesc = "Clarvix delivers professional Lead Conversion Digital Audits for local businesses. Discover why you're losing leads and get a 30-day action plan.";
  let siteUrl = "https://www.clarvix.net/";

  if (lang === 'es') {
    siteTitle = "Clarvix — Auditoría Digital de Conversión de Leads";
    siteDesc = "Clarvix ofrece Auditorías Digitales de Conversión de Leads para negocios locales. Descubre por qué pierdes leads y obtén un plan de acción de 30 días.";
    siteUrl = "https://www.clarvix.net/es.html";
  } else if (lang === 'he') {
    siteTitle = "Clarvix — ביקורת דיגיטלית להמרת לידים";
    siteDesc = "קבל דוח ביקורת מקצועי עבור העסק שלך. גלה מדוע אתה מפסיד לידים וקבל תוכנית פעולה ל-30 יום.";
    siteUrl = "https://www.clarvix.net/he.html";
  }

  const ogImage = "https://www.clarvix.net/images/hero_dashboard.png";

  // Update Title and Desc
  $('head title').text(siteTitle);
  $('head meta[name="description"]').attr('content', siteDesc);

  // Remove existing OG tags and replace them completely
  $('head meta[property^="og:"]').remove();

  const newMetaTags = [
    { property: 'og:title', content: siteTitle },
    { property: 'og:description', content: siteDesc },
    { property: 'og:type', content: 'website' },
    { property: 'og:url', content: siteUrl },
    { property: 'og:image', content: ogImage },
    { name: 'twitter:card', content: 'summary_large_image' },
    { name: 'twitter:title', content: siteTitle },
    { name: 'twitter:description', content: siteDesc },
    { name: 'twitter:image', content: ogImage },
  ];

  newMetaTags.forEach(tagData => {
    if (tagData.property) {
      $('head').append(`\n  <meta property="${tagData.property}" content="${tagData.content}" />`);
    } else if (tagData.name) {
      $('head').append(`\n  <meta name="${tagData.name}" content="${tagData.content}" />`);
    }
  });

  // Hreflang Tags
  $('head').append(`\n  <link rel="alternate" hreflang="en" href="https://www.clarvix.net/" />`);
  $('head').append(`\n  <link rel="alternate" hreflang="es" href="https://www.clarvix.net/es.html" />`);
  $('head').append(`\n  <link rel="alternate" hreflang="he" href="https://www.clarvix.net/he.html" />`);
  $('head').append(`\n  <link rel="alternate" hreflang="x-default" href="https://www.clarvix.net/" />`);

  // Schema.org JSON-LD
  const translateKey = (keyEN, keyES, keyHE) => {
    if (lang === 'es') return keyES;
    if (lang === 'he') return keyHE;
    return keyEN;
  };

  const schema = {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "name": "Clarvix",
    "url": "https://www.clarvix.net",
    "logo": "https://www.clarvix.net/images/logo.png",
    "description": siteDesc,
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "Online",
      "addressCountry": "US"
    },
    "provider": {
      "@type": "Organization",
      "name": "Clarvix"
    },
    "offerCatalog": {
      "@type": "OfferCatalog",
      "name": translateKey("Audit Packages", "Paquetes de Auditoría", "חבילות ביקורת"),
      "itemListElement": [
        {
          "@type": "Offer",
          "name": translateKey("Basic Audit", "Auditoría Básica", "ביקורת בסיסית"),
          "price": "50",
          "priceCurrency": "USD",
          "url": "https://www.fiverr.com/albertneuman402/perform-a-lead-conversion-digital-audit-with-score-benchmark-and-30-day-plan?package=1"
        },
        {
          "@type": "Offer",
          "name": translateKey("Standard Audit", "Auditoría Estándar", "ביקורת סטנדרטית"),
          "price": "80",
          "priceCurrency": "USD",
          "url": "https://www.fiverr.com/albertneuman402/perform-a-lead-conversion-digital-audit-with-score-benchmark-and-30-day-plan?package=2"
        },
        {
          "@type": "Offer",
          "name": translateKey("Premium Audit", "Auditoría Premium", "ביקורת פרימיום"),
          "price": "150",
          "priceCurrency": "USD",
          "url": "https://www.fiverr.com/albertneuman402/perform-a-lead-conversion-digital-audit-with-score-benchmark-and-30-day-plan?package=3"
        }
      ]
    }
  };

  $('head').append(`\n  <script type="application/ld+json">\n${JSON.stringify(schema, null, 2)}\n  </script>`);

  // Return the full HTML string
  return $.html();
}

const htmlEn = processHtml('en');
const htmlEs = processHtml('es');
const htmlHe = processHtml('he');

// Write out the specialized versions
fs.writeFileSync('index.html', htmlEn);
fs.writeFileSync('es.html', htmlEs);
fs.writeFileSync('he.html', htmlHe);

console.log('Successfully generated index.html (EN), es.html (ES), and he.html (HE) with SEO tags!');
