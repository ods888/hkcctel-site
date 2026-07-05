var fs = require('fs');
var handlers = require('/sessions/intelligent-upbeat-mccarthy/mnt/hkcctel/import-handlers.js');
var html = fs.readFileSync('/sessions/intelligent-upbeat-mccarthy/mnt/uploads/108GB本地365日數據卡 - 中國移動香港.html', 'utf-8');

// Test current parser
var result = handlers.parseCMHK(html);
console.log('=== CURRENT PARSER ===');
console.log('Name:', JSON.stringify(result.name));
console.log('Price:', result.price);
console.log('Image:', (result.image || '').substring(0, 80));
console.log('Summary:', (result.summary || '').substring(0, 100));
console.log('Desc len:', (result.description || '').length);

// Now test improved version
console.log('\n=== Try direct Nuxt extraction ===');
var nuxtIdx = html.indexOf('window.__NUXT__=');
if (nuxtIdx >= 0) {
    var endIdx = html.indexOf('</script>', nuxtIdx);
    var block = html.substring(nuxtIdx + 17, endIdx);

    // Extract content fields
    var contentRe = /content:"((?:[^"\\]|\\.)*)"/g;
    var matches = [];
    var m;
    while ((m = contentRe.exec(block)) !== null) {
      var decoded = m[1]
        .replace(/\\u003C/g, '<').replace(/\\u003E/g, '>')
        .replace(/\\u002F/g, '/').replace(/\\u0026/g, '&')
        .replace(/\\n/g, '\n').replace(/\\r/g, '').replace(/\\t/g, '  ')
        .replace(/\\"/g, '"').replace(/\\\\/g, '\\');
      matches.push(decoded);
    }

    console.log('Content blocks found:', matches.length);
    for (var i = 0; i < matches.length; i++) {
        console.log('Block[' + i + '] length:', matches[i].length);
    }

    // Get the main content (longest with tables)
    var mainHTML = '';
    for (var j = 0; j < matches.length; j++) {
        if (matches[j].length > 500) {
            mainHTML = matches[j];
        }
    }

    // Extract image from last block
    var lastBlock = matches[matches.length - 1] || '';
    var imgMatch = lastBlock.match(/src="([^"]+\.(?:png|jpg))"/i);
    if (imgMatch) {
        console.log('Image:', imgMatch[1]);
    }

    // Extract price
    var priceMatch = mainHTML.match(/\$(\d+)/);
    if (priceMatch) {
        console.log('First price:', priceMatch[1]);
    }
    var dedMatch = mainHTML.match(/扣除.*?\$(\d+)/);
    if (dedMatch) {
        console.log('Deduction price:', dedMatch[1]);
    }

    // Extract name from title tag
    var titleMatch = html.match(/<title>([^<]+)<\/title>/i);
    if (titleMatch) {
        console.log('Title:', titleMatch[1]);
    }
}
