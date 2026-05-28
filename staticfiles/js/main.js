// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
        const t = document.querySelector(a.getAttribute('href'));
        if (t) { e.preventDefault(); t.scrollIntoView({behavior:'smooth'}); }
    });
});

// Auto-dismiss alerts
setTimeout(() => {
    document.querySelectorAll('.alert').forEach(a => bootstrap.Alert.getOrCreateInstance(a).close());
}, 5000);

// Reading progress bar on post pages
if (document.querySelector('.post-body')) {
    const bar = document.createElement('div');
    bar.style.cssText = 'position:fixed;top:0;left:0;height:3px;background:linear-gradient(135deg,#6366f1,#ec4899);z-index:9999;transition:width .1s';
    document.body.appendChild(bar);
    window.addEventListener('scroll', () => {
        const h = document.documentElement;
        const p = (h.scrollTop / (h.scrollHeight - h.clientHeight)) * 100;
        bar.style.width = p + '%';
    });
}
