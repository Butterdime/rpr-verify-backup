const fs = require('fs-extra');
const path = require('path');

const distPath = path.join(__dirname, '../dist/rpr-client-portal/browser');
const outputPath = path.join(__dirname, '../.vercel/output');

// Create Vercel output structure
fs.ensureDirSync(path.join(outputPath, 'static'));
fs.copySync(distPath, path.join(outputPath, 'static'));

// Create config.json for SPA routing
fs.writeJsonSync(path.join(outputPath, 'config.json'), {
  version: 3,
  routes: [
    { handle: "filesystem" },
    { src: "/.*", dest: "/index.html" }
  ]
});

console.log('✅ Vercel output prepared');

