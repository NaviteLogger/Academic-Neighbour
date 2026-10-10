# Dokumentacja Użytkownika - Platforma Społecznościowa FastAPI

## Spis treści

1. [Wprowadzenie](#wprowadzenie)
2. [Rejestracja i Logowanie](#rejestracja-i-logowanie)
3. [Zarządzanie Profilem](#zarządzanie-profilem)
4. [Posty](#posty)
5. [Komentarze](#komentarze)
6. [Znajomi](#znajomi)
7. [Wiadomości](#wiadomości)
8. [Wydarzenia](#wydarzenia)
9. [Grupy](#grupy)
10. [Panel Administratora](#panel-administratora)

---

## Wprowadzenie

Witaj w platformie społecznościowej FastAPI! To aplikacja umożliwiająca komunikację z innymi użytkownikami poprzez posty, wiadomości prywatne, wydarzenia oraz grupy tematyczne. Dokumentacja ta pomoże Ci w pełni wykorzystać możliwości systemu.

### Dostęp do aplikacji

- **Adres aplikacji**: `http://localhost:8000`
- **Dokumentacja API (Swagger)**: `http://localhost:8000/docs`
- **Alternatywna dokumentacja (ReDoc)**: `http://localhost:8000/redoc`

---

## Rejestracja i Logowanie

### Rejestracja nowego konta

Aby utworzyć konto w systemie, musisz podać następujące informacje:

**Wymagane dane:**

- **Nazwa użytkownika** - unikalna, używana do logowania
- **Email** - musi być poprawnym adresem email
- **Imię** - Twoje imię
- **Nazwisko** - Twoje nazwisko
- **Hasło** - musi spełniać następujące wymagania:
  - Co najmniej 8 znaków
  - Co najmniej jedna wielka litera
  - Co najmniej jeden znak specjalny (np. !, @, #, $)

**Przykład:**

```json
{
  "username": "jankowalski",
  "email": "jan.kowalski@example.com",
  "first_name": "Jan",
  "last_name": "Kowalski",
  "password": "BezpieczneHaslo123!"
}
```

Po pomyślnej rejestracji otrzymasz automatycznie token dostępu i informacje o swoim koncie.

### Logowanie

Aby zalogować się do systemu, użyj swojej nazwy użytkownika i hasła. System zwróci token JWT (JSON Web Token), który będzie używany do autoryzacji wszystkich dalszych żądań.

**Dane do logowania:**

- **Nazwa użytkownika** (username)
- **Hasło** (password)

Token jest ważny przez określony czas i musi być dołączany do nagłówka każdego żądania wymagającego autoryzacji.

---

## Zarządzanie Profilem

### Przeglądanie profilu

Możesz przeglądać profile innych użytkowników, aby poznać ich dane podstawowe:

- Imię i nazwisko
- Nazwa użytkownika
- Email
- Data utworzenia konta
- Rola w systemie (użytkownik/administrator)

### Wyszukiwanie użytkowników

System umożliwia wyszukiwanie użytkowników po:

- Nazwie użytkownika
- Imieniu
- Nazwisku
- Adresie email

Wyniki wyszukiwania zawierają podstawowe informacje o znalezionych użytkownikach.

### Komentarze profilowe

Użytkownicy mogą zostawiać komentarze na Twoim profilu. Funkcje dostępne:

**Dodawanie komentarza:**

- Zalogowani użytkownicy mogą dodawać komentarze na profilach innych użytkowników
- Komentarze są publiczne i widoczne dla wszystkich

**Przeglądanie komentarzy:**

- Możesz zobaczyć wszystkie komentarze na swoim profilu lub profilach innych użytkowników
- Każdy komentarz zawiera informacje o autorze i dacie dodania

**Edycja komentarzy:**

- Możesz edytować tylko swoje własne komentarze
- Zmiany są natychmiast widoczne

**Usuwanie komentarzy:**

- Możesz usuwać tylko swoje własne komentarze profilowe

---

## Posty

### Tworzenie postów

Posty to główny sposób komunikacji na platformie. Możesz tworzyć posty:

- **Publiczne** - widoczne dla wszystkich użytkowników
- **W grupach** - widoczne tylko dla członków konkretnej grupy

**Wymagane informacje:**

- Treść posta (może być dowolnej długości)

**Opcjonalne:**

- ID grupy (jeśli post ma być opublikowany w grupie)

### Przeglądanie postów

System umożliwia:

## Najlepsze praktyki

### 1. Bezpieczeństwo

- Używaj silnych haseł dla kluczy JWT
- Hashuj hasła algorytmem Argon2
- Waliduj wszystkie dane wejściowe
- Używaj HTTPS w produkcji
- Implementuj rate limiting
- Regularnie aktualizuj zależności

### 2. Wydajność

- Używaj paginacji dla dużych list
- Indeksuj kolumny używane w WHERE i JOIN
- Używaj connection pooling
- Cache'uj często używane dane
- Optymalizuj zapytania SQL (unikaj N+1)

### 3. Kod

- Stosuj type hints
- Pisz testy dla wszystkich funkcji
- Dokumentuj publiczne API
- Używaj dependency injection
- Zachowaj DRY (Don't Repeat Yourself)
- Stosuj SOLID principles

### 4. Monitoring

- Loguj wszystkie ważne operacje
- Monitoruj wydajność API
- Śledź błędy i wyjątki
- Używaj health check endpoints
- Monitoruj zasoby serwera

### 5. Uwierzytelnianie i autoryzacja

- Przeglądanie wszystkich publicznych postów
- Wyświetlanie pojedynczego posta z szczegółami
- Wyświetlanie informacji o autorze posta
- Sprawdzanie liczby polubień

### Polubienia (Lajki)

Każdy zalogowany użytkownik może:

- **Polubić post** - dodaj lajka do posta, który Ci się podoba
- **Usunąć polubienie** - zmień zdanie i cofnij swój lajk
- **Sprawdzić status** - zobacz, czy już polubiłeś dany post
- **Zobaczyć liczbę polubień** - sprawdź, ile osób polubiło post

**Zasady:**

- Każdy użytkownik może polubić post tylko raz
- Można usunąć polubienie i dodać je ponownie

---

## Komentarze

### Komentowanie postów

Komentarze umożliwiają dyskusję pod postami. Dostępne funkcje:

**Dodawanie komentarza:**

- Napisz komentarz pod dowolnym postem
- Komentarze są widoczne dla wszystkich użytkowników
- Każdy komentarz zawiera datę i informacje o autorze

**Przeglądanie komentarzy:**

- Zobacz wszystkie komentarze pod konkretnym postem
- Komentarze wyświetlane są z informacjami o autorach
- Komentarze są sortowane chronologicznie

**Edycja komentarzy:**

- Możesz edytować tylko swoje własne komentarze
- Zmiany są natychmiast widoczne dla wszystkich użytkowników
- System nie zapisuje historii edycji

**Usuwanie komentarzy:**

- Możesz usunąć tylko swoje własne komentarze
- Usunięcie jest trwałe i nieodwracalne

---

## Znajomi

System znajomości umożliwia nawiązywanie relacji z innymi użytkownikami platformy.

### Zaproszenia do znajomych

**Wysyłanie zaproszenia:**

- Możesz wysłać zaproszenie do znajomych do dowolnego użytkownika
- Nie możesz wysłać zaproszenia do samego siebie
- Jeśli użytkownik już otrzymał Twoje zaproszenie, nie możesz wysłać kolejnego

**Stany zaproszeń:**

- **Oczekujące (pending)** - zaproszenie zostało wysłane, ale nie zostało jeszcze zaakceptowane
- **Zaakceptowane (accepted)** - użytkownicy są znajomymi
- **Odrzucone (declined)** - zaproszenie zostało odrzucone

### Zarządzanie zaproszeniami

**Akceptowanie zaproszenia:**

- Możesz zaakceptować zaproszenie, które otrzymałeś od innego użytkownika
- Po zaakceptowaniu oboje użytkownicy stajecie się znajomymi

**Odrzucanie zaproszenia:**

- Możesz odrzucić niechciane zaproszenie
- Odrzucone zaproszenie może zostać wysłane ponownie przez nadawcę

**Anulowanie zaproszenia:**

- Możesz anulować zaproszenie, które wysłałeś, zanim zostanie zaakceptowane
- Po anulowaniu możesz wysłać nowe zaproszenie

**Usuwanie znajomego:**

- Możesz usunąć użytkownika ze swojej listy znajomych
- Działa to również w drugą stronę - usunięcie jest dwustronne
- Po usunięciu możecie ponownie wysłać sobie zaproszenia

### Przeglądanie znajomych

**Lista znajomych:**

- **Zaakceptowani znajomi** - zobacz wszystkich swoich znajomych
- **Otrzymane zaproszenia** - zobacz zaproszenia, które musisz rozpatrzyć
- **Wysłane zaproszenia** - zobacz zaproszenia, które wysłałeś i czekają na odpowiedź

---

## Wiadomości

System wiadomości umożliwia prywatną komunikację z innymi użytkownikami w czasie rzeczywistym.

### Konwersacje

**Tworzenie konwersacji:**

- Możesz rozpocząć konwersację z dowolnym użytkownikiem platformy
- Nie możesz utworzyć konwersacji ze sobą samym
- Jeśli konwersacja z danym użytkownikiem już istnieje, system zwróci istniejącą konwersację
- Każda konwersacja ma automatycznie generowany tytuł

**Przeglądanie konwersacji:**

- Zobacz listę wszystkich swoich konwersacji
- Każda konwersacja zawiera informacje o uczestnikach
- Możesz sprawdzić, kto jest uczestnikiem konkretnej konwersacji

**Wyświetlanie wiadomości:**

- Zobacz wszystkie wiadomości w konwersacji
- Wiadomości są sortowane chronologicznie
- Każda wiadomość zawiera treść, informacje o nadawcy i datę wysłania

### Wysyłanie wiadomości

**Tworzenie wiadomości:**

- Wyślij wiadomość tekstową w ramach istniejącej konwersacji
- Musisz być uczestnikiem konwersacji, aby wysłać wiadomość
- Wiadomości są dostarczane natychmiast

### Komunikacja w czasie rzeczywistym (WebSocket)

Platforma obsługuje komunikację w czasie rzeczywistym poprzez WebSocket:

**Funkcje czasu rzeczywistego:**

- Natychmiastowe dostarczanie wiadomości bez odświeżania strony
- Powiadomienia o nowych wiadomościach
- Status online/offline użytkowników
- Potwierdzenia dostarczenia wiadomości

**Jak to działa:**

1. Zaloguj się do systemu i otrzymaj token JWT
2. Połącz się z WebSocket używając tokena
3. Wszystkie nowe wiadomości będą automatycznie dostarczane
4. Możesz wysyłać wiadomości przez WebSocket

**Dodawanie uczestników:**

- Możesz dodawać nowych uczestników do istniejącej konwersacji
- Tylko uczestnicy konwersacji mogą dodawać nowe osoby

---

## Wydarzenia

System wydarzeń umożliwia organizowanie i uczestniczenie w wydarzeniach.

### Tworzenie wydarzeń

Każdy zalogowany użytkownik może tworzyć wydarzenia. Wymagane informacje:

- **Tytuł** - nazwa wydarzenia
- **Opis** - szczegółowy opis wydarzenia
- **Lokalizacja** - miejsce wydarzenia
- **Data rozpoczęcia** - kiedy wydarzenie się rozpoczyna
- **Data zakończenia** - kiedy wydarzenie się kończy

**Zasady:**

- Data zakończenia musi być późniejsza niż data rozpoczęcia
- Jesteś automatycznie organizatorem swojego wydarzenia

### Przeglądanie wydarzeń

**Lista wydarzeń:**

- Zobacz wszystkie nadchodzące wydarzenia
- Przeglądaj szczegóły każdego wydarzenia
- Sprawdź listę uczestników

**Informacje o wydarzeniu:**

- Tytuł i opis
- Organizator
- Lokalizacja
- Daty rozpoczęcia i zakończenia
- Lista uczestników z ich statusami

### Uczestnictwo w wydarzeniach

**Dołączanie do wydarzenia:**

- Możesz dołączyć do dowolnego wydarzenia
- Wybierz swój status uczestnictwa:
  - **Biorę udział (attending)** - potwierdzasz obecność
  - **Zainteresowany (interested)** - możesz wziąć udział
  - **Nie biorę udziału (not_attending)** - nie możesz uczestniczyć

**Zmiana statusu:**

- Możesz zmienić swój status uczestnictwa w dowolnym momencie
- Status jest widoczny dla innych użytkowników

**Opuszczanie wydarzenia:**

- Możesz zrezygnować z uczestnictwa w wydarzeniu
- Twoje dane zostaną usunięte z listy uczestników

### Zarządzanie wydarzeniami

**Edycja wydarzenia:**

- Tylko organizator może edytować wydarzenie
- Możesz zmienić wszystkie informacje oprócz organizatora
- Zmiany są natychmiast widoczne dla wszystkich użytkowników

**Usuwanie wydarzenia:**

- Tylko organizator może usunąć wydarzenie
- Usunięcie jest trwałe i nieodwracalne
- Wszyscy uczestnicy tracą dostęp do wydarzenia

**Usuwanie uczestnika:**

- Organizator może usunąć uczestnika z wydarzenia
- Przydatne w przypadku naruszeń lub pełnej liczby miejsc

---

## Grupy

System grup umożliwia tworzenie społeczności o wspólnych zainteresowaniach.

### Tworzenie grup

**Zakładanie grupy:**

- Każdy zalogowany użytkownik może utworzyć grupę
- Podaj nazwę i opis grupy
- Jako założyciel automatycznie stajesz się członkiem

**Wymagane informacje:**

- **Nazwa** - unikalna nazwa grupy
- **Opis** - cel i tematyka grupy

### Przeglądanie grup

**Lista grup:**

- Zobacz wszystkie dostępne grupy na platformie
- Przeglądaj szczegóły każdej grupy
- Sprawdź listę członków

**Szczegóły grupy:**

- Nazwa i opis
- Założyciel grupy
- Data utworzenia
- Lista członków
- Posty opublikowane w grupie

### Członkostwo w grupach

**Dołączanie do grupy:**

- Możesz dołączyć do dowolnej grupy
- Członkostwo jest natychmiastowe (brak procesu zatwierdzania)
- Nie możesz dołączyć do tej samej grupy dwukrotnie

**Opuszczanie grupy:**

- Możesz opuścić grupę w dowolnym momencie
- Tracisz dostęp do postów grupowych po opuszczeniu

**Przeglądanie członków:**

- Zobacz listę wszystkich członków grupy
- Sprawdź, kto jest założycielem

### Posty w grupach

**Tworzenie postów grupowych:**

- Tylko członkowie mogą tworzyć posty w grupie
- Posty są widoczne tylko dla członków grupy
- Podaj treść posta i ID grupy

**Przeglądanie postów:**

- Musisz być członkiem grupy, aby zobaczyć jej posty
- Posty są sortowane chronologicznie
- Każdy post zawiera informacje o autorze

---

## Panel Administratora

### Funkcje administratorskie

Administratorzy mają rozszerzone uprawnienia w systemie:

**Zarządzanie użytkownikami:**

- **Przeglądanie wszystkich użytkowników** - zobacz pełną listę użytkowników w systemie
- **Wyszukiwanie użytkowników** - znajdź użytkownika po nazwie użytkownika lub emailu
- **Szczegóły użytkownika** - zobacz pełne informacje o dowolnym użytkowniku

**Dodatkowe uprawnienia:**

- Dostęp do wszystkich danych w systemie
- Możliwość moderacji treści
- Zarządzanie kontami użytkowników

### Jak zostać administratorem?

Role użytkowników są przypisywane na poziomie bazy danych. Standardowo nowe konta mają rolę "user". Aby uzyskać rolę administratora, skontaktuj się z administratorem systemu.

---

## Najlepsze praktyki i wskazówki

### Bezpieczeństwo

1. **Hasła:**
   - Używaj silnych haseł (min. 8 znaków, wielkie litery, znaki specjalne)
   - Nigdy nie udostępniaj swojego hasła innym osobom
   - Regularnie zmieniaj hasło

2. **Token dostępu:**
   - Nie udostępniaj swojego tokena JWT nikomu
   - Token wygasa po określonym czasie - zaloguj się ponownie
   - Wyloguj się po zakończeniu pracy

### Korzystanie z platformy

1. **Treści:**
   - Publikuj wartościowe i konstruktywne posty
   - Szanuj innych użytkowników w komentarzach
   - Nie publikuj treści obraźliwych lub nielegalnych

2. **Komunikacja:**
   - Bądź uprzejmy w wiadomościach prywatnych
   - Szanuj prywatność innych użytkowników
   - Zgłaszaj nadużycia administratorom

3. **Znajomi:**
   - Wysyłaj zaproszenia tylko do osób, które znasz lub chcesz poznać
   - Szybko odpowiadaj na otrzymane zaproszenia
   - Możesz odmówić niechcianych zaproszeń

4. **Wydarzenia:**
   - Aktualizuj swój status uczestnictwa jeśli się zmieni
   - Szanuj organizatorów i innych uczestników
   - Jeśli organizujesz wydarzenie, dbaj o aktualne informacje

5. **Grupy:**
   - Publikuj posty zgodne z tematyką grupy
   - Szanuj zasady ustalone przez założyciela
   - Aktywnie uczestniczuj w dyskusjach

---

## Rozwiązywanie problemów

### Nie mogę się zalogować

- Sprawdź, czy nazwa użytkownika i hasło są poprawne
- Upewnij się, że Twoje konto jest aktywne
- Skontaktuj się z administratorem jeśli problem persystuje

### Nie widzę swoich postów/wiadomości

- Sprawdź połączenie internetowe
- Odśwież stronę lub aplikację
- Upewnij się, że jesteś zalogowany

### Nie mogę wykonać określonej akcji

- Sprawdź, czy masz odpowiednie uprawnienia
- Upewnij się, że Twój token dostępu nie wygasł
- Niektóre akcje wymagają specjalnych uprawnień (np. edycja tylko swoich treści)

### Problemy z czasem rzeczywistym (WebSocket)

- Sprawdź połączenie internetowe
- Upewnij się, że używasz poprawnego tokena JWT
- Zrestartuj połączenie WebSocket
- Sprawdź, czy jesteś uczestnikiem konwersacji

---

## Kontakt i wsparcie

Jeśli masz pytania, problemy lub sugestie dotyczące platformy:

1. **Dokumentacja API**: Odwiedź `http://localhost:8000/docs` dla szczegółowej dokumentacji technicznej
2. **Administrator**: Skontaktuj się z administratorem systemu
3. **Zgłaszanie błędów**: Opisz problem jak najdokładniej, podając kroki do jego odtworzenia

---

## Historia zmian

### Aktualna wersja

- System zarządzania użytkownikami
- Posty i komentarze
- System znajomych
- Wiadomości prywatne z WebSocket
- Wydarzenia
- Grupy tematyczne
- Panel administratora
- Uwierzytelnianie JWT

---

**Dziękujemy za korzystanie z naszej platformy! Życzymy miłego użytkowania! 🚀**
