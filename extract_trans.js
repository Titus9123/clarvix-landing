const fs = require('fs');
const cheerio = require('cheerio');
const html = fs.readFileSync('index.html', 'utf8');
const $ = cheerio.load(html);

const texts = [];
function walk(node) {
  if (node.type === 'text') {
    const txt = node.data.trim();
    if (txt.length > 0 && !txt.match(/^\{|^\</) && txt !== 'EN' && txt !== '|' && txt !== 'ES' && txt !== '→' && txt !== '✓' && txt !== '↓' && txt !== '✕') {
      texts.push(txt);
    }
  } else if (node.type === 'tag' && node.name !== 'script' && node.name !== 'style') {
    if (node.attribs && node.attribs.placeholder) {
      texts.push(node.attribs.placeholder.trim());
    }
    (node.children || []).forEach(walk);
  }
}
walk($('body')[0]);
fs.writeFileSync('texts.json', JSON.stringify(Array.from(new Set(texts)), null, 2));
