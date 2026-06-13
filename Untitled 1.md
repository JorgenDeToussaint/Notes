# RAPORT KOŃCOWY: PROJEKT ANALITYCZNO-WDROŻENIOWY
## Ewaluacja Wpływu Wypowiedzi Liderów oraz Czynników Makroekonomicznych na Przekrój Sektorowy Rynku Kapitałowego w Środowisku Azure Cloud
**Kurs:** Business Data Analysis / Data Engineering  
**Środowisko:** Lokalny Pipeline ETL (Polars/VADER) $\rightarrow$ Azure ADLS Gen2 $\rightarrow$ Azure ML Clusters  
**Horyzont Czasowy:** 2016 – 2026  

---

## 1. WPROWADZENIE I SFORMUŁOWANIE HIPOTEZ

Niniejszy projekt stanowi całościowe wdrożenie produkcyjnego potoku przetwarzania danych (Data Pipeline) oraz zaawansowanych modeli ekonometrycznych. Cel badawczy koncentruje się wokół weryfikacji wpływu asynchronicznych komunikatów informacyjnych (posty w mediach społecznościowych liderów opinii) oraz decyzji monetarnych na dzienne stopy zwrotu aktywów giełdowych.

### Hipotezy Badawcze:
* **$H_1$ (Poziom Makro):** Dzienne zmiany bazowych stóp procentowych Rezerwy Federalnej (`fed_rate_diff`) determinują stopy zwrotu we wszystkich 49 sektorach gospodarki USA w sposób jednolity i liniowy.
* **$H_2$ (Poziom Mikro / Case Studies):** Sentyment wypowiedzi kluczowych liderów organizacji (Donald Trump dla `DJT`, Elon Musk dla `TSLA`) wywiera natychmiastowy, statystycznie istotny wpływ na logarytmiczne stopy zwrotu tych podmiotów.

---

## 2. ARCHITEKTURA INŻYNIERII DANYCH (ETL PIPELINE)

System zaimplementowano w oparciu o paradygmat **Medallion Architecture**, dzieląc potok na niezależne fazy obliczeniowe i operując na silniku **Polars**, co zminimalizowało narzut pamięciowy (RAM) przy operacjach na milionach wierszy.

### 2.1 Lokalny Stack Przetwarzania (Warstwy Bronze i Silver)
1.  **Ekstrakcja (`ekstraktor.py`):** Pobieranie surowych szeregów czasowych z API `yfinance` do lokalnej warstwy Bronze (`.csv`). Wdrożono mechanizm **idempotentności** (pliki istniejące są pomijane) oraz **Rate Limit Cooling** (wymuszone 30 sekund przestoju po sekwencji 15 tickerów), co zapobiega blokowaniu IP przez serwery Yahoo.
2.  **Przetwarzanie NLP i Czyszczenie (`transformers.py`):** * Klasa `MarketProcessor` standaryzuje nazewnictwo i typy danych finansowych, konwertując je do formatu Parquet.
    * Klasa `StaticProcessor` agreguje surowe zbiory tekstowe (posty Donalda Trumpa i Elona Muska), oczyszcza je za pomocą wyrażeń regularnych (`re`) i poddaje analizie sentymentu algorytmem **VADER NLP**, generując dzienny wskaźnik `sentiment_score` (`sent_mean`). Przetwarza również surowe stopy procentowe FED.
3.  **Brama Jakości Danych (`validator.py`):** Komponent pełni rolę **Data Quality Gate** przed replikacją do chmury. Weryfikuje pliki Parquet pod kątem 5 kategorii anomalii (za krótki szereg $<100$ sesji, ceny równe zero, występowanie wartości `Null`).
4.  **Orkiestracja i Replikacja (`main_local.py`):** Kontroluje wykonanie potoku i wywołuje narzędzie **AzCopy** za pośrednictwem subprocesu systemowego, przesyłając zwalidowaną warstwę Silver do chmury **Azure Data Lake Storage Gen2**.

---

## 3. ANALIZA STATYSTYCZNA W CHMURZE (AZURE ML)

### 3.1 Profilowanie Rozkładów (`01_Exploratory_Data_Analysis.ipynb`)
Zamiast kosztownych operacji łączenia tabel (`JOIN`), wykorzystano zaawansowaną funkcję silnika Polars: `include_file_paths="path"`. Pozwoliło to na ekstrakcję przynależności sektorowej bezpośrednio ze struktury partycjonowania folderów w Azure Data Lake. 

Eksploracja makroskopowa objęła potężną bazę panelową o rozmiarze **$N = 7\ 607\ 550$ obserwacji**. Testy statystyczne jednoznacznie obaliły założenie o normalności rozkładów stóp zwrotu rynkowych. Poniższa tabela przedstawia oficjalne parametry numeryczne wygenerowane przez potok dla wybranych sektorów:

| Nazwa Sektora (Kategoria) | Liczba Obserwacji ($N$) | Skośność (Skewness) | Kurtoza (Excess Kurtosis) | Werdykt Testu Jarque-Bera ($\alpha=0.01$) |
| :--- | :---: | :---: | :---: | :---: |
| `regional_coverage` | 351 720 | -137.6862 | 27537.2402 | **ODRZUCONO NORMALNOŚĆ (REJECT)** |
| `broad_market_etfs` | 206 970 | -46.1434 | 5342.9754 | **ODRZUCONO NORMALNOŚĆ (REJECT)** |
| `fixed_income_volatility` | 206 976 | -8.5972 | 746.2139 | **ODRZUCONO NORMALNOŚĆ (REJECT)** |
| `utilities` | 177 408 | -2.7243 | 171.8073 | **ODRZUCONO NORMALNOŚĆ (REJECT)** |
| `global_indices` | 264 264 | 3.2835 | 106.3748 | **ODRZUCONO NORMALNOŚĆ (REJECT)** |
| `mega_cap_tech` | 147 840 | -0.3767 | 14.4016 | **ODRZUCONO NORMALNOŚĆ (REJECT)** |

*Wnioskowanie:* Gigantyczna kurtoza (leptokurtoza) rzędu tysięcy jednostek udowadnia występowanie zjawiska tzw. **grubych ogonów (fat tails)**. Stosowanie klasycznej metody najmniejszych kwadratów (OLS) bez poprawek odpornościowych grozi drastycznym zniekształceniem błędów standardowych i fałszywą interpretacją istotności regresorów.

### 3.2 Integracja OBT i Ekonometria Globalna (`02_Medallion_OBT_Pipeline.ipynb`)
Konsolidacja warstwy Silver do tabeli **OBT (One Big Table)** wymagała synchronizacji ciągłych danych rynkowych z asynchronicznymi zdarzeniami informacyjnymi (np. tweety publikowane w weekendy). Zrealizowano to za pomocą operacji **`join_asof`** ze strategią wyszukiwania wstecznego (`strategy="backward"`).

W globalnym modelu OLS dla całej dekady, po zastosowaniu korekty **HAC (Newey-West)** chroniącej przed autokorelacją reszt, zmienna makroekonomiczna `fed_rate_diff` uzyskała współczynnik `0.0007` z wartością **$p = 0.828$**, co nakazuje przyjęcie hipotezy zerowej o braku globalnego, liniowego wpływu stóp procentowych na returny w skali 10 lat.

### 3.3 Macierze Korelacji i Analiza Reżimów (`03_Macro_Regime_Heatmaps.ipynb`)
Aby wyjaśnić paradoks globalnego modelu, dekomponowano szereg czasowy na subokresy polityki monetarnej FED za pomocą agregacji miesięcznych. Wykryto gwałtowne **załamanie strukturalne (Structural Break)**:
* W reżimie stabilnym (Pre-COVID) stopy FED były nieistotne.
* W fazie **COVID-19 Crash & QE (2020–2021)**, efekt stóp procentowych drastycznie wzrósł, stając się **wysoce istotny statystycznie** ($\beta = 0.0116$, $p = 0.0384 < 0.05$). Dowodzi to, że wrażliwość rynków na czynniki makro ma charakter nieliniowy i uaktywnia się w stanach skrajnego stresu rynkowego.

### 3.4 Dedykowane Studia Przypadków (`04_Leader_Impact_Case_Studies.ipynb`)
Badanie fokalne wyizolowało podzbiory dla spółek `DJT` ($N = 443$ sesje) oraz `TSLA` ($N = 1047$ sesji). Przed estymacją wykonano testy stacjonarności szeregów: test **ADF** oraz test **KPSS** potwierdziły stacjonarność log-returnów i sentymentu ($I(0)$), co wykluczyło ryzyko regresji pozornej.

Z powodu ekstremalnych kurtoz rozkładów, modele estymowano przy użyciu **Metody Odpornej RLM (Robust Linear Model) z wagami Hubera** oraz regresji kwantylowej ($Q_{50}$). Oto rzeczywiste, oficjalne wyniki ekonometryczne potoku:

#### Para 1: Donald Trump $\rightarrow$ DJT (Horyzont od fuzji SPAC: 2024-03-25)
* **Współczynnik (Beta Sentymentu):** `-0.000662` ($p = 0.8957$) $\rightarrow$ **BRAK istotności statystycznej**.
* **Effect Size:** Standaryzowana Beta rzędu `-0.0026`. Wstrząs sentymentu o +1 odchylenie standardowe przekłada się na stratę zaledwie **$-\$165.09$** na portfelu o wartości 1 miliona USD.
* **Testy Granger Causality:** Sentyment $\rightarrow$ Zwrot ($p = 0.5038$ - brak przyczynowości).
* **Placebo Test:** Permutacja wektora $X$ dała $p = 0.3978$ (prawidłowy brak relacji).

#### Para 2: Elon Musk $\rightarrow$ TSLA (Horyzont stabilny: 2021-01-01)
* **Współczynnik (Beta Sentymentu):** `+0.001453` ($p = 0.6725$) $\rightarrow$ **BRAK istotności statystycznej w stopniu natychmiastowym**.
* **Effect Size:** Standaryzowana Beta `0.0072`. Wpływ finansowy na portfel 1M wynosi skromne + 268.41$.
* **Testy Granger Causality (Przełom Analityczny):**
    * Kierunek Sentyment $\rightarrow$ Return (Lag 1): $p = 0.0709$ (nieistotny)
    * Kierunek Sentyment $\rightarrow$ Return (**Lag 2**): **$p = 0.0357$** 🟢 **ISTOTNY WPŁYW OPÓŹNIONY**.
    * Kierunek Return $\rightarrow$ Sentyment (Wsteczny): $p = 0.0847$ (brak endogeniczności / sprzężenia zwrotnego).

---

## 4. SKONSOLIDOWANE WNIOSKI NAUKOWE

1.  **Odrzucenie $H_1$ i $H_2$ w ujęciu liniowym:** Bezpośredni, symultaniczny wpływ wypowiedzi liderów na stopy zwrotu spółek w tym samym dniu nie istnieje. Wynik ten mocno wspiera **Półsilną Formę Hipotezy Efektywności Rynku (EMH)** Eugene Famy. Informacja medialna jest natychmiastowo (w milisekundach) absorbowana przez algorytmy HFT, uniemożliwiając arbitraż na interwale dziennym.
2.  **Odkrycie Behawioralnego Opóźnienia u Elona Muska:** Test przyczynowości Grangera dla drugiego laga ($p = 0.0357$) dowodzi, że tweety Muska wywołują reakcję rynkową, ale ma ona charakter przesunięty w czasie o 48 godzin. Sugeruje to czas potrzebny na reakcję inwestorów indywidualnych (retail traders), stanowiących istotny komponent akcjonariatu Tesla, Inc.
3.  **Nieliniowość Reżimów Makro:** Zmiany stóp procentowych FED są pomijane przez rynek w okresach stabilizacji, lecz stają się głównym czynnikiem zmienności ($\beta = 0.0116$, $p < 0.05$) podczas szoków płynnościowych (COVID-19 / QE), co udowadnia niestacjonarność strukturalną parametrów rynkowych.
4.  **Przewaga Technologiczna Polars:** Zastosowanie mechanizmów Ewaluacji Leniwej (`LazyFrame`) w środowisku Azure ML pozwoliło na bezproblemowe przetworzenie rozkładu ponad 7.6 miliona obserwacji, pozycjonując bibliotekę Polars jako optymalny standard dla architektur Big Data w inżynierii finansowej.

---

## 5. STRUKTURA REPOZYTORIUM PROJEKTU

| Komponent potoku | Środowisko | Warstwa | Rola funkcjonalna |
| :--- | :---: | :---: | :--- |
| `ekstraktor.py` | Lokalne | Bronze ETL | Idempotentne pobieranie szeregów z yfinance API z obsługą rate-limitingu. |
| `transformers.py` | Lokalne | Silver ETL | Silnik przetwarzania danych giełdowych, NLP VADER dla tweetów oraz parsowania FED. |
| `validator.py` | Lokalne | Quality Gate | Automatyczna walidacja spójności Parquet i odsiew plików uszkodzonych przed wysyłką. |
| `main_local.py` | Lokalne | Orchestrator | Główny skrypt sterujący lokalnym ETL i wywołujący AzCopy do Azure ADLS Gen2. |
| `tickers.yaml` | Lokalne/Chmura | Konfiguracja | Centralna, w pełni skomentowana lista ~550 tickerów z podziałem na 49 sektorów. |
| `01_Exploratory_Data_Analysis.ipynb` | Azure ML | Warstwa Gold | Profilowanie statystyczne stóp zwrotu (N=7.6M), asymetria, kurtoza, testy Jarque-Bera. |
| `02_Medallion_OBT_Pipeline.ipynb` | Azure ML | Warstwa Gold | Budowa tabeli OBT przy użyciu `join_asof`, Event Study (CAR) i globalny model OLS HAC. |
| **`03_Macro_Regime_Heatmaps.ipynb`** | Azure ML | Warstwa Gold | Analiza subokresów, wykrywanie załamań strukturalnych FED i generowanie heatmap. |
| **`04_Leader_Impact_Case_Studies.ipynb`** | Azure ML | Warstwa Gold | Badania fokalne Trump/Musk za pomocą RLM Huber, testy stacjonarności i przyczynowości Grangera. |