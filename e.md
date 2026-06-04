# Projekt ekonometryczny — Wariant I

## Model liniowy z doborem zmiennych metodą Hellwiga

  

##### Tomasz Sokołowski, Mateusz Zalewski

---

  

## 1. Opis danych i specyfikacja modelu

  

Przedmiotem analizy jest badanie zależności pomiędzy produktem krajowym brutto (PKB) a wybranymi makroekonomicznymi zmiennymi strukturalnymi dla 16 województw Polski w 2007 roku. Dane źródłowe pochodzą z Rocznika Statystycznego Województw 2006/2007.

  

* **Zmienna objaśniana:**

    * `y` – PKB województwa w milionach złotych (ceny bieżące).

* **Zmienne objaśniające (finalny zestaw po redukcji):**

    * `x1` – nakłady inwestycyjne w województwie w mln zł (ceny bieżące).

    * `x2` – wartość brutto aktywów stałych w województwie w mln zł (ceny stałe).

    * `x4` – produkcja sprzedana przemysłu w województwie w mln zł (ceny bieżące).

  

Liczba obserwacji: **16**.

  

---

  

## 2. Dobór zmiennych i uzasadnienie wariantu trójzmiennego

  

W celu wyłonienia optymalnego podzbioru zmiennych objaśniających zastosowano sformalizowaną procedurę – **metodę Hellwiga** (wskaźników pojemności informacyjnej) za pomocą funkcji `hellwig()` z pakietu `mbstats`.

  

Algorytm przetestował wszystkie $2^5 - 1 = 31$ kombinacji kandydatek i jako matematycznie najefektywniejszy wskazał układ czterozmienny **x1 + x2 + x3 + x4** o najwyższej integralnej pojemności informacyjnej $H = 0.9926$.

  

### Konieczność manualnej refaktoryzacji (Krytyka wskaźnika Hellwiga)

Mimo najwyższego wskaźnika $H$, wstępna estymacja modelu czterozmiennego wykazała dwa krytyczne błędy systemowe:

1.  **Nieistotność statystyczna zmiennej x3 (zatrudnienie):** wartość p-value wynosiła aż $0.131$, co wykluczało tę zmienną z poprawnego modelu.

2.  **Potężna współliniowość (Multikolinearność):** Wskaźnik VIF dla zatrudnienia ($x3$) wynosił $21.22$, a dla inwestycji ($x1$) aż $25.66$. Wynika to z faktu, że w ujęciu regionalnym nakłady inwestycyjne i wielkość zatrudnienia niosą niemal identyczną informację (są skrajnie skorelowane: $r = 0.9672$).

  

**Decyzja analityczna:** Świadomie odrzucono teoretyczne wskazanie Hellwiga i usunięto z układu zmienną $x3$. Uzyskano stabilny, poprawny matematycznie i ekonomicznie **wariant trójzmienny (x1 + x2 + x4)**.

  

---

  

## 3. Estymacja i interpretacja modelu

  

### 3.1. Zapis formalny modelu (MNK)

  

Oszacowane równanie regresji liniowej uzyskane metodą najmniejszych kwadratów przyjmuje postać:

  

$$\hat{y} = 2541 + 4.528 \cdot x_1 + 0.0505 \cdot x_2 + 0.3784 \cdot x_4$$

  

Z uwzględnieniem błędów standardowych oszacowań parametrów strukturalnych (w nawiasach):

  

$$\hat{y} = 2541_{(1223)} + 4.528_{(0.464)} \cdot x_1 + 0.0505_{(0.0197)} \cdot x_2 + 0.3784_{(0.0621)} \cdot x_4$$

  

### 3.2. Interpretacja ekonomiczna współczynników

  

* **Wyraz wolny ($a_0 = 2541$):** Przy braku nakładów inwestycyjnych, zerowych aktywach stałych i braku produkcji przemysłowej bazowe PKB wynosi 2541 mln zł. Parametr nie posiada głębszego uzasadnienia ekonomicznego (jest to ekstrapolacja poza obszar próby).

* **Współczynnik przy $x_1$ ($a_1 = 4.528$):** Jeśli nakłady inwestycyjne w województwie wzrosną o 1 mln zł, to PKB tego województwa wzrośnie przeciętnie o **4.528 mln zł**, przy założeniu *ceteris paribus*. Znak dodatni jest w pełni zgodny z teorią makroekonomii (inwestycje bezpośrednio kreują wartość dodaną).

* **Współczynnik przy $x_2$ ($a_2 = 0.0505$):** Jeśli wartość brutto aktywów stałych wzrośnie o 1 mln zł, to PKB województwa wzrośnie przeciętnie o **0.0505 mln zł** ($50.5$ tys. zł), przy założeniu *ceteris paribus*. Aktywa stałe reprezentują zaangażowany w regionie kapitał produkcyjny.

* **Współczynnik przy $x_4$ ($a_4 = 0.3784$):** Jeśli produkcja sprzedana przemysłu wzrośnie o 1 mln zł, to PKB województwa wzrośnie przeciętnie o **0.3784 mln zł**, przy założeniu *ceteris paribus*. Przemysł pozostaje jednym z głównych motorów napędowych gospodarki regionalnej.

  

### 3.3. Jakość dopasowania i struktura stochastyczna

  

* **Współczynnik determinacji $R^2 = 0.9970$ ($99.70\%$):** Model wykazuje wyjątkowo wysoki stopień dopasowania – wyjaśnia aż $99.70\%$ zmienności PKB województw. Tak wysoki wynik jest naturalny dla modeli opartych na przekrojowych danych makroekonomicznych w Polsce, gdzie skrajne dysproporcje skali (np. Mazowieckie vs Opolskie) idealnie porządkują liniowy trend.

* **Skorygowany $R^2_{adj} = 0.9963$:** Potwierdza, że wysokie dopasowanie nie jest wynikiem przeładowania modelu zbędnymi zmiennymi.

* **Odchylenie standardowe reszt $S_e = 3029$ mln zł:** Szacując PKB województwa na podstawie wygenerowanego modelu, mylimy się przeciętnie o $\pm 3029$ mln zł.

  

---

  

## 4. Weryfikacja statystyczna i diagnostyka modelu

  

### 4.1. Badanie istotności parametrów (Test t-Studenta)

  

| Zmienna | Współczynnik | Błąd std. | Wartość t | p-value | Istotność (brak H0 przy $\alpha=0.05$) |

| :--- | :---: | :---: | :---: | :---: | :---: |

| **(Intercept)** | 2541 | 1223 | 2.078 | 0.0598 | Nieistotny (na granicy błędu) |

| **x1 (Inwestycje)** | 4.528 | 0.464 | 9.753 | $4.69 \cdot 10^{-7}$ | **Statystycznie istotny (***) ** |

| **x2 (Aktywa)** | 0.0505 | 0.0197 | 2.561 | 0.0250 | **Statystycznie istotny (*)** |

| **x4 (Produkcja)** | 0.3784 | 0.0621 | 6.090 | $5.41 \cdot 10^{-5}$ | **Statystycznie istotny (***) ** |

  

**Wniosek:** Wszystkie zmienne objaśniające są w pełni istotne statystycznie na klasycznym poziomie istotności $5\%$.

  

### 4.2. Istotność modelu jako całości (Test F Snedecora)

* Statystyka testowa: $F = 1338$ na 3 oraz 12 stopniach swobody.

* Wartość $p\text{-value} = 2.053 \cdot 10^{-15} \ll 0.05$.

* **Wniosek:** Odrzucamy hipotezę zerową. Model jako całość jest skrajnie istotny statystycznie.

  

### 4.3. Badanie współliniowości (Wskaźnik VIF)

* `x1` (Inwestycje): **VIF = 16.223**

* `x2` (Aktywa stałe): **VIF = 5.301**

* `x4` (Produkcja przemysłu): **VIF = 10.206**

  

**Wniosek:** Usunięcie zmiennej $x3$ przyniosło zamierzony skutek. Żaden ze wskaźników VIF nie przekracza krytycznego progu błędu równego 20. Współliniowość została skutecznie zredukowana.

  

### 4.4. Testy założeń struktury stochastycznej

  

* **Normalność rozkładu reszt (Test Shapiro-Wilka):**

    * Statystyka $W = 0.9150$, $p\text{-value} = 0.1402$.

    * *Wniosek:* Ponieważ $p > 0.05$, brak podstaw do odrzucenia $H_0$. Składnik losowy ma **rokład normalny**.

* **Homoskedastyczność wariancji reszt (Test Goldfelda-Quandta):**

    * Statystyka $GQ = 0.7389$, $p\text{-value} = 0.6118$.

    * *Wniosek:* Ponieważ $p > 0.05$, brak podstaw do odrzucenia $H_0$. Wariancja reszt jest stabilna i jednorodna (**homoskedastyczność**).

* **Autokorelacja składnika losowego (Testy Durbina-Watsona i Breuscha-Godfreya):**

    * Test D-W: $DW = 1.5152$, $p\text{-value} = 0.1601$.

    * Test B-G (rząd 1): $LM = 0.0119$, $p\text{-value} = 0.9130$.

    * *Wniosek:* Brak podstaw do odrzucenia $H_0$. W składniku losowym **nie występuje autokorelacja rzędu I**.

  

---

  

## 5. Analiza obserwacji nietypowych

  

### 5.1. Obserwacje odstające ($|z| > 2$)

Analiza reszt standaryzowanych wykazała jedną wyraźną anomalię:

* **Województwo Wielkopolskie:** Reszta standaryzowana wynosi **2.6725**.

  

*Uzasadnienie merytoryczne:* Model drastycznie niedoszacowuje PKB Wielkopolski. Wynika to z potężnej anomalii w danych wejściowych – podana w roczniku wartość brutto aktywów stałych dla Wielkopolski ($16\ 854$ mln zł) jest nienaturalnie niska na tle regionów o zbliżonej skali (np. Małopolskie ma $131\ 041$ mln zł). Może to sugerować błąd redakcyjny w źródłowym roczniku GUS.

  

### 5.2. Obserwacje wpływowe (Leverage > próg $2k/n = 0.5$)

Trzy obiekty przekraczają krytyczny próg dźwigni:

1.  **Wielkopolskie** (Leverage = 0.9539) – wynik wspomnianej anomalii aktywów.

2.  **Śląskie** (Leverage = 0.9268) – wynik potężnej, niespotykanej w innych regionach koncentracji produkcji przemysłowej ($x4$).

3.  **Mazowieckie** (Leverage = 0.8463) – efekt skrajnej dominacji makroekonomicznej (najwyższe wartości inwestycji, PKB i produkcji).

  

**Decyzja końcowa:** Mimo statusu punktów wpływowych i odstających, obserwacje te pozostawiono w modelu. Próba jest mała ($n=16$), a usunięcie trzech kluczowych gospodarczo województw całkowicie wypaczyłoby poznawczy sens analizy makroekonomicznej Polski.

  

---

  

## 6. Podsumowanie i wnioski

  

Zrefaktorowany model trójzmienny okazał się pełnym sukcesem analitycznym. Spełnia on absolutnie wszystkie teoretyczne założenia klasycznej metody najmniejszych kwadratów (KMNK).

  

Dzięki manualnej eliminacji zmiennej zatrudnienia, usunięto problem korelacji wewnętrznej, uzyskując czyste, wysoce istotne i stabilne interpretacje współczynników ekonomicznych. Model w 99.70% opisuje rzeczywistość regionalną i stanowi rzetelną podstawę do wnioskowania statystycznego.