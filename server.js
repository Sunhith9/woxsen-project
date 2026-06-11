const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;

const MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'text/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.ttf': 'font/ttf',
    '.eot': 'application/vnd.ms-fontobject'
};

const server = http.createServer((req, res) => {
    // Parse URL and clean query params
    const parsedUrl = new URL(req.url, `http://${req.headers.host}`);
    let pathname = parsedUrl.pathname;

    logger(`Request: ${req.method} ${req.url}`);

    // Route matching like Nginx
    if (pathname === '/') {
        serveFile(path.join(__dirname, 'landing.html'), res);
    } else if (pathname === '/admin') {
        serveFile(path.join(__dirname, 'Woxsen_Admin_Panel.html'), res);
    } else if (pathname === '/department') {
        serveFile(path.join(__dirname, 'department_portal.html'), res);
    } else if (pathname === '/student') {
        serveFile(path.join(__dirname, 'index.html'), res);
    } else {
        // Serve static asset file directly
        const filePath = path.join(__dirname, pathname);
        // Security check: ensure file is within root directory
        if (!filePath.startsWith(__dirname)) {
            res.statusCode = 403;
            res.end('Forbidden');
            return;
        }
        serveFile(filePath, res);
    }
});

function serveFile(filePath, res) {
    fs.stat(filePath, (err, stats) => {
        if (err || !stats.isFile()) {
            res.statusCode = 404;
            res.setHeader('Content-Type', 'text/plain');
            res.end('404 Not Found');
            return;
        }

        const ext = path.extname(filePath).toLowerCase();
        const contentType = MIME_TYPES[ext] || 'application/octet-stream';

        res.statusCode = 200;
        res.setHeader('Content-Type', contentType);
        
        const readStream = fs.createReadStream(filePath);
        readStream.on('error', (streamErr) => {
            logger(`Stream error: ${streamErr.message}`);
            if (!res.headersSent) {
                res.statusCode = 500;
                res.setHeader('Content-Type', 'text/plain');
                res.end('Internal Server Error');
            }
        });
        readStream.pipe(res);
    });
}

function logger(msg) {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${msg}`);
}

server.listen(PORT, () => {
    console.log('\n==================================================');
    console.log(`🚀 Woxsen University Frontend Server running at:`);
    console.log(`   http://localhost:${PORT}/`);
    console.log(`\nRoutes mapped:`);
    console.log(`   /           -> landing.html`);
    console.log(`   /student    -> index.html`);
    console.log(`   /admin      -> Woxsen_Admin_Panel.html`);
    console.log(`   /department -> department_portal.html`);
    console.log('==================================================\n');
});
