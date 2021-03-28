Nume: STIUCA Roxana-Elena
Grupa: 335CB

# Tema 1 ASC - Marketplace

### Organizare
Pe langa scheletul oferit de echipa ASC, programul se foloseste de 2 clase:
- SafeList, care intern pastreaza o lista, dar garanteaza prelucrarea sa de
catre un singur thread la un moment de timp. Desi operatiile de tip append si
remove sunt deja thread-safe in python, clasa SafeList ofera inca un nivel
de siguranta. De asemenea, permite setarea unui maxsize, peste care nu se
poate insera (se arunca exceptia Full) prin folosirea operatiei put. Exista
si operatia put_anyway, care nu tine cont de maxsize si insereaza oricum.
- Cart, care simuleaza un cos de cumparaturi. Elementele sale sunt produse,
care au asociat si producer_id (deci cosul de cumparaturi retine si de la ce
producator provine fiecare produsul, a.i. in caz de returnare sa stie in coada
carui producator trebuie).

#### Organizare Producer
- se inregistreaza si primeste un ID;
- cat timp programul ruleaza, el cicleaza prin lista sa de produse,
produce pe rand din fiecare tip si incearca sa publice cate un produs;
daca nu reuseste sa publice un produs, el asteapta un timp si incearca iar.

#### Organizare Consumer
pentru fiecare drum la magazin:
- ia un cos de cumparaturi (identificat prin cart_id);
- adauga si retrage produse in/din cos; in cazul adaugarii, e posibil sa nu
gaseasca un produs, caz in care asteapta un timp si incearca iar;
- plaseaza comanda si printeaza lista de articole cumparate.

### Implementare
Implementarea propriu-zisa se gaseste in Marketplace.
Detalii:
- cand un consumator adauga un produs in cosul sau, este retinut si ID-ul
producatorului; astfel, daca returneaza produsul, el va fi returnat in coada
producatorului initial.
- ID-urile producatorilor sunt oferite printr-un numar intreg, ce se
incrementeaza la fiecare nou producator; pt. fiecare nou producator, este
adaugat si o coada noua de produse (initial vida) asociata ID-ului sau.
- similar pt. ID-urile cosurilor de cumparaturi.

#### Sincronizare
Pentru ca in enunt si in implementare, producatorii lucreaza fiecare cu lista/
coada sa de produse, nu apar probleme de concurenta de tip acces comun al
mai multor producatori. Singurele probleme ce trebuie evitate sunt:
- nu putem avea 2 producatori care sa se inregistreze in acelasi timp;
- nu putem avea 2 consumatori care sa primeasca un cos de cumparaturi in
acelasi timp;
- nu putem avea 2 consumatori care sa incerce sa ia acelasi produs sau ca un
producator sa incerce sa puna in coada sa de produse in acelasi timp cand
un consumator returneaza un produs (posibil ca producatorul sa nu aiba loc).

Aceste probleme sunt rezolvate astfel:
- cozile de produse pt. fiecare producator sunt de tipul SafeList (ca sa poata
fi accesate in sigurante si de producator si de oricati clienti);
- pentru generarea ID-ului unui producator, este folosit un obiect Lock;
- pentru generarea ID-ului unui cos de cumparaturi, este folosit un obiect
Lock.

Cand un consumator cauta un obiect, se uita pe rand prin cozile tuturor
consumatorilor. Ca sa evitam situatia //rara// in care fix atunci se
inregistreaza un producator si poate inca nu are coada creata, am folosit
producer_id_generator_lock pentru a obtine numarul de producatori actuali.

### Git
https://github.com/roxanastiuca/ASC-Marketplace

### Observatii
Datorita separarii zonei de lucru a producatorilor, elementele de sincronizare
sunt minime.
Am sincronizat toate operatiile din SafeList pentru a fi sigura de
corectitudine. Checkerul mergea si fara niciun lock in SafeList, dar am
citit ca in unele implementari Python, nu toate operatiile pe liste sunt
thread-safe.