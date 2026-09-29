from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from pathlib import Path
import os, base64

ROOT = Path(__file__).parent
VIDEO = ROOT / 'intro.mp4'
if not VIDEO.exists():
    parts=[]
    for p in sorted(ROOT.glob('video.part*')):
        parts.append(p.read_text(encoding='utf-8').strip())
    if parts:
        VIDEO.write_bytes(base64.b64decode(''.join(parts)))

POPUP = '''<style>#vp{position:fixed;left:18px;bottom:18px;z-index:2147483647;width:min(280px,calc(100vw - 36px));border-radius:18px;overflow:hidden;background:#111;box-shadow:0 14px 40px rgba(0,0,0,.28);opacity:0;transform:translateY(16px);transition:.28s ease}#vp.show{opacity:1;transform:none}#vp video{display:block;width:100%;height:auto;max-height:58vh;object-fit:cover;background:#000}#vpc{position:absolute;top:8px;right:8px;display:flex;gap:7px}#vp button{border:0;border-radius:999px;width:36px;height:36px;background:rgba(0,0,0,.58);color:#fff;font-size:18px;cursor:pointer}@media(max-width:640px){#vp{left:12px;bottom:12px;width:min(210px,calc(100vw - 24px));border-radius:15px}#vp button{width:32px;height:32px;font-size:16px}}</style><div id="vp"><video id="vv" autoplay muted loop playsinline preload="auto" src="/intro.mp4"></video><div id="vpc"><button id="vs">🔇</button><button id="vc">×</button></div></div><script>(function(){const b=document.getElementById('vp'),v=document.getElementById('vv'),s=document.getElementById('vs'),c=document.getElementById('vc');setTimeout(()=>{b.classList.add('show');v.play().catch(()=>{});},500);s.onclick=()=>{v.muted=!v.muted;s.textContent=v.muted?'🔇':'🔊'};c.onclick=()=>{v.pause();b.remove()}})();</script>'''

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/intro.mp4':
            if not VIDEO.exists():
                self.send_response(404); self.end_headers(); return
            data=VIDEO.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type','video/mp4')
            self.send_header('Content-Length',str(len(data)))
            self.send_header('Cache-Control','public,max-age=86400')
            self.end_headers(); self.wfile.write(data); return
        req=Request('https://vladstryuk.ru/', headers={'User-Agent':'Mozilla/5.0'})
        with urlopen(req, timeout=20) as r:
            raw=r.read().decode('utf-8','ignore')
        lower=raw.lower()
        if '<head>' in lower:
            i=lower.find('<head>')+6
            raw=raw[:i]+'<base href="https://vladstryuk.ru/">'+raw[i:]
        lower=raw.lower()
        if '</body>' in lower:
            i=lower.rfind('</body>'); raw=raw[:i]+POPUP+raw[i:]
        else:
            raw+=POPUP
        data=raw.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type','text/html; charset=utf-8')
        self.send_header('Content-Length',str(len(data)))
        self.end_headers(); self.wfile.write(data)

ThreadingHTTPServer(('0.0.0.0', int(os.environ.get('PORT','10000'))), H).serve_forever()
