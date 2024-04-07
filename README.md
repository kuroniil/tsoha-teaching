# Opetussovellus

Sovelluksen avulla opettajat voivat järjestää verkkokursseja johon opiskelijat voivat liittyä. Kursseilla on automaattisesti tarkastettavia tehtäviä sekä tekstimateriaalia.

Sovelluksen ominaisuuksia ovat:

* Käyttäjä voi kirjautua sisään ja ulos sekä luoda uuden tunnuksen.
* Opiskelija näkee listan kursseista ja voi liittyä kurssille.
* Opiskelija voi lukea kurssin tekstimateriaalia sekä ratkoa kurssin tehtäviä.
* Opiskelija pystyy näkemään tilaston, mitkä kurssin tehtävät hän on ratkonut.
* Opettaja pystyy luomaan uuden kurssin, muuttamaan olemassa olevaa kurssia ja poistamaan kurssin.
* Opettaja pystyy lisäämään kurssille tekstimateriaalia ja tehtäviä. Tehtävä voi olla ainakin monivalinta tai tekstikenttä, johon tulee kirjoittaa oikea vastaus.
* Opettaja pystyy näkemään kurssistaan tilaston, keitä opiskelijoita on kurssilla ja mitkä kurssin tehtävät kukin on ratkonut.

Sovelluksen kaikki perusominaisuudet ovat nyt valmiina.

# Käynnistysohjeet

Kloonaa repositorio ja luo sen juurikansioon .env-tiedosto. Muokkaa .env-tiedosto seuraavanlaiseksi:

```
DATABASE_URL=<tietokannan-osoite-tietokoneella>
SECRET_KEY=<keksi-salainen-avain>
```  
Aktivoi virtuaaliympäristö ja asenna sovelluksen riippuvuudet:

```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r ./requirements.txt
```

Määritä tietokannan skeema:
```
$ psql < schema.sql
```

Nyt sovelluksen voi käynnistää komennolla
```
$ flask run
```
