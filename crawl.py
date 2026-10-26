# /// script
# requires-python = ">=3.10"
# ///
import json, sys, os, io, glob, zipfile, time, threading, random, urllib.request, urllib.error, concurrent.futures as cf

BASE = "https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3221"
DIR = os.environ.get("OUT_DIR") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")
UFS = "rj pr sc sp mg rs ba pe ce go pa ma pb rn al se pi es df mt ms am ro to ac ap rr zz".split()
RPS = float(os.environ.get("RPS", "10"))
WORKERS = int(os.environ.get("WORKERS", "24"))


class Limiter:
    def __init__(self, rps):
        self.rps, self.lock, self.next = rps, threading.Lock(), time.monotonic()

    def wait(self):
        with self.lock:
            now = time.monotonic()
            self.next = max(self.next, now) + 1 / self.rps
            d = self.next - now - 1 / self.rps
        if d > 0:
            time.sleep(d)

    def slow(self):
        with self.lock:
            self.rps = max(2, self.rps * 0.7)
            self.next = time.monotonic() + 30
        log(f"backoff: rps={self.rps:.1f}")


lim = Limiter(RPS)
plock = threading.Lock()


def log(msg):
    with plock:
        print(time.strftime("%H:%M:%S"), msg, flush=True)


def get(url):
    for i in range(8):
        lim.wait()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            return urllib.request.urlopen(req, timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise
            if e.code in (403, 429):
                lim.slow()
            time.sleep(min(60, 2 ** i) + random.random())
        except Exception:
            if i >= 2:
                lim.slow()
            time.sleep(min(60, 2 ** i) + random.random())
    raise RuntimeError(f"falhou: {url}")


def parse(raw):
    z = zipfile.ZipFile(io.BytesIO(raw))
    r = {"arquivos": z.namelist(), "pronta": [], "encerramento": [], "votos_tarde": [], "votos": 0, "modelo": None}
    for nm in z.namelist():
        for line in z.read(nm).decode("latin1").splitlines():
            p = line.split("\t")
            if len(p) < 5 or not p[0].startswith("25/10/2026"):
                continue
            t, ev = p[0][11:], p[4]
            if ev == "O voto do eleitor foi computado":
                r["votos"] += 1
                if t >= "13:00:00":
                    r["votos_tarde"].append(t)
            elif ev == "Urna pronta para receber votos":
                r["pronta"].append(t)
            elif ev == "Procedimento de encerramento confirmado":
                r["encerramento"].append(t)
            elif ev.startswith("Identificação do Modelo de Urna"):
                r["modelo"] = ev.split(":")[-1].strip()
    return r


def secao(uf, mu, nm, zo, se):
    d = f"{BASE}/dados/{uf}/{mu}/{zo}/{se}"
    out = {"uf": uf, "cd_mun": mu, "municipio": nm, "zona": zo, "secao": se}
    try:
        aux = json.loads(get(f"{d}/p003221-{uf}-m{mu}-z{zo}-s{se}-aux.json"))
    except urllib.error.HTTPError as e:
        return {**out, "erro": f"aux {e.code}"}
    out["st"] = aux.get("st")
    hs = aux.get("hashes", [])
    if not hs:
        return {**out, "erro": "sem hashes"}
    h = hs[-1]
    out["hash_st"], out["recebido"] = h.get("st"), h.get("hr")
    lg = [a["nm"] for a in h.get("arq", []) if a.get("tp") == "log"]
    if not lg:
        return {**out, "erro": "sem log", "tipos": [a.get("tp") for a in h.get("arq", [])]}
    try:
        return {**out, **parse(get(f"{d}/{h['hash']}/{lg[0]}"))}
    except urllib.error.HTTPError as e:
        return {**out, "erro": f"log {e.code}"}
    except zipfile.BadZipFile:
        return {**out, "erro": "zip invalido"}


def main():
    ufs = sys.argv[1:] or UFS
    os.makedirs(DIR, exist_ok=True)
    with cf.ThreadPoolExecutor(WORKERS) as ex:
        for uf in ufs:
            path = os.path.join(DIR, f"{uf}.jsonl")
            feito = set()
            if os.path.exists(path):
                for l in open(path):
                    try:
                        r = json.loads(l)
                    except json.JSONDecodeError:
                        continue
                    if not str(r.get("erro", "")).startswith("excecao"):
                        feito.add((r["cd_mun"], r["zona"], r["secao"]))
            cs = json.loads(get(f"{BASE}/config/{uf}/{uf}-p003221-cs.json"))
            todas = [(m["cd"], m["nm"], z["cd"], s["ns"]) for m in cs["abr"][0]["mu"] for z in m["zon"] for s in z["sec"]]
            falta = [t for t in todas if (t[0], t[2], t[3]) not in feito]
            log(f"{uf}: {len(todas)} seções, {len(falta)} a baixar")
            t0 = time.time()
            with open(path, "a") as f:
                futs = {ex.submit(secao, uf, *t): t for t in falta}
                for i, fu in enumerate(cf.as_completed(futs), 1):
                    try:
                        r = fu.result()
                    except Exception as e:
                        mu, nm, zo, se = futs[fu]
                        r = {"uf": uf, "cd_mun": mu, "municipio": nm, "zona": zo, "secao": se, "erro": f"excecao {e}"}
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
                    if i % 2000 == 0:
                        f.flush()
                        log(f"{uf}: {i}/{len(falta)} ({i / (time.time() - t0):.1f} seç/s)")
            log(f"{uf}: concluído")


if __name__ == "__main__":
    main()
