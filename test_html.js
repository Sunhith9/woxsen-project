const fs = require('fs');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;

const html = fs.readFileSync('c:/Users/Kande Sunhith/Downloads/gym-app-v3.html', 'utf8');

const dom = new JSDOM(html, { runScripts: "dangerously" });

dom.window.addEventListener('error', (event) => {
    console.error('JSDOM Error:', event.error);
});
