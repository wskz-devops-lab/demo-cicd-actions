# Poradnik: Automatyczne wdrażanie Cloudflare Workers przez CI/CD

Ten dokument wyjaśnia krok po kroku, **czym są Cloudflare Workers** i jak połączyć je z **Forgejo Actions** (Twój własny serwer) oraz **GitHub Actions**, aby każdy `git push` automatycznie publikował nową wersję aplikacji w chmurze.

---

## 1. Czym jest Cloudflare Worker? (W 3 zdaniach)

Tradycyjnie, aby wystawić API lub stronę WWW, musisz mieć serwer (VPS/VM/kontener), skonfigurować Nginx/Docker i pilnować aktualizacji. **Cloudflare Workers** to platforma *serverless* (FaaS): piszesz krótką funkcję w JavaScript/TypeScript (lub Python/WebAssembly), a Cloudflare uruchamia ją bezpośrednio w swoich centrach danych na całym świecie (Edge) — **darmowy plan daje 100 000 zapytań dziennie** i natychmiastowy adres `https://twoja-nazwa.twoj-nick.workers.dev`.

Do zarządzania Workerami z terminala służy oficjalne narzędzie **`wrangler`** (CLI od Cloudflare).

---

## 2. Jednorazowa konfiguracja w panelu Cloudflare

Aby pipeline CI/CD mógł wdrożyć kod w Twoim imieniu (bez ręcznego logowania w przeglądarce), potrzebuje dwóch danych: **Account ID** oraz **API Token**.

### Krok 2.1. Pobranie Account ID
1. Zaloguj się do [dash.cloudflare.com](https://dash.cloudflare.com).
2. Z menu po lewej stronie wybierz **Compute (Workers) → Workers & Pages**.
3. Po prawej stronie ekranu znajdziesz sekcję **Account ID** — skopiuj ten 32-znakowy ciąg.

### Krok 2.2. Wygenerowanie API Tokena
1. Kliknij ikonę profilu (prawy górny róg) → **My Profile → API Tokens → Create Token**.
2. Wybierz gotowy szablon **Edit Cloudflare Workers** (*Use template*).
3. W sekcji *Account Resources* wybierz swoje konto.
4. Kliknij **Continue to summary → Create Token** i **skopiuj wygenerowany token** (wyświetla się tylko raz!).

---

## 3. Dodanie sekretów w Forgejo i/lub GitHubie

**Nigdy nie wpisuj tokenów bezpośrednio w plikach YAML ani `wrangler.toml`!** Zamiast tego zapisz je w zaszyfrowanym magazynie sekretów repozytorium:

- **W Forgejo (`dev.zarnecki.org`):**
  `Ustawienia repozytorium → Actions → Sekrety → Dodaj sekret`
- **W GitHubie (`github.com`):**
  `Settings → Secrets and variables → Actions → New repository secret`

Dodaj dokładnie dwa sekrety:
| Nazwa sekretu | Wartość |
|---|---|
| `CLOUDFLARE_API_TOKEN` | Token skopiowany w kroku 2.2 |
| `CLOUDFLARE_ACCOUNT_ID` | Account ID skopiowane w kroku 2.1 |

---

## 4. Jak działa wdrożenie w naszym repozytorium?

W katalogu [`cloudflare-worker-demo/`](./cloudflare-worker-demo/) znajdują się 3 minimalne pliki:
- `src/index.js` — kod Workera odpowiadający JSON-em na `/` oraz `/health`.
- `wrangler.toml` — nazwa Workera i data kompatybilności.
- `package.json` — zależność `wrangler`.

Pliki workflow:
- Dla Forgejo: [`.forgejo/workflows/deploy-cloudflare-worker.yml`](./.forgejo/workflows/deploy-cloudflare-worker.yml)
- Dla GitHuba: [`.github/workflows/deploy-cloudflare-worker.yml`](./.github/workflows/deploy-cloudflare-worker.yml)

### Co dzieje się po `git push`?
1. Filtr `paths: ['cloudflare-worker-demo/**']` pilnuje, aby ten workflow uruchamiał się **tylko wtedy**, gdy zmienisz coś w kodzie Workera (lub możesz go odpalić ręcznie przyciskiem **Run workflow** dzięki `workflow_dispatch`).
2. Runner pobiera kod (`actions/checkout@v4`).
3. Instaluje `wrangler` (`npm install`).
4. Wywołuje `npx wrangler deploy` (lub `cloudflare/wrangler-action@v3`) ze zmiennymi środowiskowymi `CLOUDFLARE_API_TOKEN` i `CLOUDFLARE_ACCOUNT_ID`.
5. Po ~10–15 sekundach nowa wersja jest już aktywna pod adresem `*.workers.dev`!

---

## 5. Przydatne komendy lokalne (dla studentów)

Jeśli chcesz przetestować Workera lokalnie na swoim komputerze przed wysłaniem go do CI/CD:
```bash
cd cloudflare-worker-demo
npm install
npx wrangler dev       # uruchamia lokalny serwer testowy na http://localhost:8787
npx wrangler deploy    # ręczne wdrożenie (wymaga wcześniejszego: npx wrangler login)
```
