# Scenariusze pokazowe CI/CD dla studentów (Live Demo + GitHub)

Poniższy zestaw to gotowy scenariusz na 30–45 minut zajęć lub warsztatów koła naukowego oraz **instrukcja krok po kroku, jak uruchomić to samodzielnie na własnym koncie GitHub**.

> **Jak przygotować konkretny system (GitHub / Forgejo / Cloudflare)?**  
> Zobacz osobną instrukcję krok po kroku dla każdej platformy: [`KONFIGURACJA_PLATFORM.md`](./KONFIGURACJA_PLATFORM.md).

---

## Część 0: Jak to zrobić po swojej stronie na GitHubie (dla studenta)

Jeśli realizujesz projekt na **własnym koncie GitHub** (`github.com`), wykonaj poniższe 5 kroków:

1. **Utwórz własną kopię repozytorium:**
   - Kliknij **Fork** w repozytorium koła (`wskz-devops-lab/demo-cicd-actions`) **albo** utwórz własne nowe repozytorium na GitHubie i wrzuć do niego pliki (pamiętając o katalogu `.github/workflows/ci.yml`).
   - Sklonuj je lokalnie:
     ```bash
     git clone git@github.com:TWOJ_LOGIN/demo-cicd-actions.git
     cd demo-cicd-actions
     ```
2. **Włącz GitHub Actions (ważne przy forku!):**
   - Na GitHubie forki mają domyślnie wyłączone workflow ze względów bezpieczeństwa.
   - Wejdź w zakładkę **Actions** w swoim repozytorium i kliknij zielony przycisk **I understand my workflows, go ahead and enable them**.
3. **Dodaj sekrety (tylko jeśli wdrażasz Cloudflare Workers):**
   - Wejdź w **Settings → Secrets and variables → Actions → New repository secret**.
   - Dodaj `CLOUDFLARE_API_TOKEN` oraz `CLOUDFLARE_ACCOUNT_ID` (szczegóły w [`CLOUDFLARE_WORKERS_PORADNIK.md`](./CLOUDFLARE_WORKERS_PORADNIK.md)).
4. **Włącz ochronę gałęzi `main` (Branch Protection — dobra praktyka zespołowa):**
   - Wejdź w **Settings → Branches → Add branch protection rule** (lub *Rulesets*).
   - Wpisz `main`, zaznacz **Require a pull request before merging** oraz **Require status checks to pass before merging** (wybierz `test-and-report`).
   - Od teraz GitHub zablokuje przycisk *Merge*, jeśli testy w CI są czerwone!
5. **Przetestuj w praktyce:**
   - Wypchnij zmianę na gałąź (`git push`) i obserwuj zakładkę **Actions** — GitHub automatycznie uruchomi maszynę `ubuntu-latest` i przetestuje kod na Pythonie 3.11 oraz 3.12 równolegle.

---

## Scenariusz 1: „Zielony build” — pierwsze uruchomienie (5 min)

**Cel:** Pokazać, że zwykły `git push` uruchamia automatyczną weryfikację w chmurze / na serwerze koła bez ręcznego logowania się po SSH.

1. Otwórz zakładkę **Actions** w repozytorium w Forgejo (lub GitHub).
2. W terminalu uruchom lokalnie testy, żeby pokazać punkt odniesienia:
   ```bash
   python3 -m pytest -v
   python3 rocket_telemetry.py
   ```
3. Zmień nazwę misji w `rocket_telemetry.py` (np. `PROXMOX-ORBIT-01` → `WSKZ-ORBIT-02`), zrób commit i push:
   ```bash
   git add rocket_telemetry.py
   git commit -m "Zmiana nazwy misji na WSKZ-ORBIT-02"
   git push
   ```
4. **Co pokazujesz na ekranie:** W ciągu ~1–2 sekund pojawia się nowy przebieg, a po ~9 sekundach wszystkie kroki świecą na zielono. Rozwiń krok `🚀 Raport gotowości misji`, żeby pokazać kolorową ramkę wygenerowaną przez runnera.

---

## Scenariusz 2: „Czerwony build” — CI jako strażnik jakości (10 min)

**Cel:** Udowodnić studentom, że pipeline nie jest tylko „ozdobą”, ale realną barierą chroniącą gałąź `main` przed błędami.

1. Wprowadź celowy błąd w logice `rocket_telemetry.py` (np. zmień znak `+` lub usuń walidację `if isp <= 0:`) albo zepsuj asercję w `test_rocket.py`:
   ```bash
   sed -i 's/3200.50 m\/s/9999.99 m\/s/' test_rocket.py
   git commit -am "Celowy błąd w teście (demo czerwonego CI)"
   git push
   ```
2. **Co pokazujesz na ekranie:**
   - Krok `🧪 Uruchomienie testów jednostkowych (pytest)` kończy się na **czerwono** (`exit code 1`).
   - Krok `🚀 Raport gotowości misji` **NIE wykonał się** (został pominięty) — zepsuty kod nie poszedł dalej!
   - Wykonał się natomiast krok `🚨 Alert w razie awarii (demo)` dzięki warunkowi `if: failure()`.
3. Cofnij błąd czysto przez `git revert` (dobra praktyka zamiast `reset --hard` na współdzielonej gałęzi):
   ```bash
   git revert --no-edit HEAD
   git push
   ```
   Pipeline wraca na zielono.

---

## Scenariusz 3: Pull Request Gate — ochrona `main` w pracy zespołowej (10 min)

**Cel:** Pokazać jak pracuje zespół 2–5 osób, żeby nikt nie zepsuł głównej gałęzi koledze.

1. Utwórz nową gałąź i wprowadź drobną poprawkę:
   ```bash
   git checkout -b feature/nowy-test
   # dodaj prosty test do test_rocket.py
   git commit -am "feat: dodatkowy test marginesu paliwa"
   git push -u origin feature/nowy-test
   ```
2. W interfejsie Forgejo / GitHub utwórz **Pull Request** z `feature/nowy-test` do `main`.
3. **Co pokazujesz na ekranie:** Trigger `pull_request:` automatycznie odpala testy **zanim** ktokolwiek kliknie *Merge*. Jeśli włączysz w ustawieniach repozytorium regułę **Branch Protection** (*Require status checks to pass*), przycisk *Merge* będzie wręcz zablokowany, dopóki CI nie zaświeci na zielono.

---

## Scenariusz 4: Co jeszcze warto pokazać studentom? (Rozszerzenia)

Poniżej znajdują się krótkie fragmenty YAML, które można dopisać do workflow na żywo, aby zilustrować kolejne koncepcje DevOps:

### A. Ręczne uruchamianie z parametrami (`workflow_dispatch` + `inputs`)
Pozwala stworzyć „przycisk w panelu”, w którym użytkownik wybiera np. środowisko wdrożenia:
```yaml
on:
  workflow_dispatch:
    inputs:
      mission_name:
        description: "Nazwa misji do raportu"
        required: true
        default: "WSKZ-DEMO-01"
```
W kroku `run:` odczytujemy to przez `${{ inputs.mission_name }}`.

### B. Przekazywanie sekretów (bezpieczeństwo)
Nigdy nie trzymamy haseł, kluczy SSH ani tokenów API w kodzie. W `Settings → Actions → Secrets` dodajemy np. `API_KEY`, a w YAML używamy go tak:
```yaml
- name: Wysłanie powiadomienia
  env:
    MOJ_SEKRET: ${{ secrets.API_KEY }}
  run: echo "Długość sekretu: ${#MOJ_SEKRET}" # Logi automatycznie maskują wartość jako ***
```

### C. Zapisywanie artefaktów (raportów, paczek, wyników testów)
Jeśli pipeline wygeneruje plik (np. raport HTML z testów lub zbudowany plik `.zip` / `.pdf`), można go zachować do pobrania w UI:
```yaml
- name: Zapisz raport jako artefakt
  if: always() # Zapisz nawet jeśli testy padły!
  uses: actions/upload-artifact@v4
  with:
    name: raport-testow
    path: report.html
```

### D. Warunek `if:` na gałąź lub status
- `if: github.ref == 'refs/heads/main'` — krok wdrożenia (deploy) odpala się **tylko** po scaleniu do `main`, nigdy na Pull Requestach.
- `if: failure()` — odpala się tylko przy błędzie (np. alert na Mattermost/Zulip).
- `if: always()` — odpala się zawsze (np. sprzątanie zasobów tymczasowych).

### E. Dlaczego w Forgejo instalowaliśmy `pytest` przez `apt-get`, a na GitHubie nie?
To świetne pytanie dla studentów do zrozumienia **obrazów kontenerowych**:
- Nasz własny runner w Proxmoxie (`CT 100`) uruchamia zadania w lekkim kontenerze `node:22-bookworm` (Debian + Node.js, bez Pythona `pytest`).
- GitHub na `ubuntu-latest` daje cięższą maszynę wirtualną z setkami preinstalowanych narzędzi (Python, Docker, Go, Rust, Terraform).
- **Wniosek inżynierski:** Jeśli w kole będziemy często uruchamiać testy w Pythonie lub Terraformie na własnym runnerze, zamiast za każdym razem robić `apt-get install`, możemy zbudować **własny obraz Docker/Podman** (np. `wskz-ci-python:3.12`) i podpiąć go w konfiguracji runnera!
