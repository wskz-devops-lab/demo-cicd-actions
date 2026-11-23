# Jak przygotować projekt pod konkretny system CI/CD (GitHub, Forgejo, Cloudflare)

Ten przewodnik pokazuje **krok po kroku, osobno dla każdej platformy**, co musisz skonfigurować po stronie serwisu oraz w plikach swojego repozytorium, aby pipeline zadziałał od pierwszego `git push`.

---

## 1. GitHub Actions (ścieżka nr 1 dla studentów)

GitHub udostępnia darmowe maszyny wirtualne w chmurze (`ubuntu-latest`), więc nie musisz stawiać własnego runnera.

### Co przygotować w repozytorium (pliki):
1. Utwórz katalog `.github/workflows/` i wrzuć do niego plik YAML (np. [`.github/workflows/ci.yml`](./.github/workflows/ci.yml)).
2. Ustaw runner w chmurze GitHuba:
   ```yaml
   runs-on: ubuntu-latest
   ```
3. Do Pythona użyj gotowej akcji `actions/setup-python@v5` (szybko i bez `apt-get`).

### Co wyklikać na stronie `github.com`:
1. **Włącz Actions (obowiązkowe po zrobieniu Forka!):**  
   Zakładka **Actions** → kliknij **I understand my workflows, go ahead and enable them**.
2. **Dodaj sekrety (jeśli pipeline ich wymaga):**  
   **Settings → Secrets and variables → Actions → New repository secret**.
3. **Włącz ochronę gałęzi `main` (opcjonalnie, zalecane w zespole):**  
   **Settings → Branches → Add branch protection rule** → wpisz `main` → zaznacz **Require status checks to pass before merging** i wskaż nazwę zadania (np. `test-and-report`).

---

## 2. Forgejo Actions / Codeberg (własny serwer lub Codeberg)

Forgejo (oraz oparty na nim Codeberg) ma składnię YAML niemal identyczną z GitHub Actions, ale działa na **Twoich własnych runnerach** (np. nasz kontener `CT 100` na Proxmoxie) albo na publicznych runnerach Codeberga.

### Co przygotować w repozytorium (pliki):
1. Utwórz katalog `.forgejo/workflows/` i wrzuć do niego plik YAML (np. [`.forgejo/workflows/ci.yml`](./.forgejo/workflows/ci.yml)).  
   *(Wskazówka: Forgejo potrafi też czytać `.github/workflows/`, ale własny katalog `.forgejo/workflows/` pozwala mieć osobną konfigurację runnera niż na GitHubie).*
2. Dopasuj etykietę `runs-on:` do swojego runnera:
   - Na serwerze koła (`CT 100` z Podmanem): `runs-on: linux-amd64`
   - Na Codeberg (jeśli używasz publicznego runnera): `runs-on: docker`
3. **Uwaga na lekkie kontenery:** własny runner często startuje w minimalnym obrazie (np. `node:22-bookworm`), w którym nie ma `python3` ani `pytest` — dlatego w kroku `run:` doinstalowujemy je przez `apt-get` (zobacz [`.forgejo/workflows/ci.yml`](./.forgejo/workflows/ci.yml)).

### Co wyklikać w panelu Forgejo (`dev.zarnecki.org` / `codeberg.org`):
1. **Włącz Actions w repozytorium:**  
   **Ustawienia repozytorium → Actions → Włącz (Enable)** *(jeśli zakładka Actions nie jest widoczna)*.
2. **Sprawdź, czy runner jest Online:**  
   W panelu administratora lub organizacji: **Actions → Runners** (status musi być zielony / `Idle`).
3. **Dodaj sekrety (jeśli są potrzebne):**  
   **Ustawienia repozytorium → Actions → Sekrety → Dodaj sekret**.

---

## 3. Cloudflare (Workers + Wrangler CLI — dodatek wdrożeniowy)

Cloudflare nie jest systemem Git, lecz platformą docelową (*deployment target*), na którą **GitHub Actions** lub **Forgejo Actions** wypychają gotowy kod za pomocą narzędzia **`wrangler`**.

*(Uwaga na nazewnictwo: **`wrangler`** służy do wdrażania aplikacji **Cloudflare Workers**, natomiast **`cloudflared`** to demon do wystawiania lokalnych usług przez **Cloudflare Tunnel**).*

### Co przygotować na koncie Cloudflare (`dash.cloudflare.com`):
1. **Pobierz `Account ID`:**  
   **Workers & Pages** → po prawej stronie skopiuj 32-znakowy **Account ID**.
2. **Wygeneruj `API Token`:**  
   Ikona profilu → **My Profile → API Tokens → Create Token** → wybierz szablon **Edit Cloudflare Workers** → skopiuj token.

### Co przygotować w repozytorium (pliki):
1. Kod Workera oraz plik konfiguracyjny `wrangler.toml` (przykład w [`cloudflare-worker-demo/`](./cloudflare-worker-demo/)).
2. Plik workflow wyzwalany przy zmianach w katalogu Workera:
   - Dla GitHuba: [`.github/workflows/deploy-cloudflare-worker.yml`](./.github/workflows/deploy-cloudflare-worker.yml) (używa `cloudflare/wrangler-action@v3`)
   - Dla Forgejo: [`.forgejo/workflows/deploy-cloudflare-worker.yml`](./.forgejo/workflows/deploy-cloudflare-worker.yml) (używa `npx wrangler deploy`)

### Co dodać w sekretach GitHub / Forgejo:
W ustawieniach repozytorium (**Secrets**) dodaj dokładnie dwa wpisy:
- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

Pełny opis i lokalne komendy testowe (`npx wrangler dev`) znajdziesz w [`CLOUDFLARE_WORKERS_PORADNIK.md`](./CLOUDFLARE_WORKERS_PORADNIK.md).
