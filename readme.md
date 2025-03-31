# badmintellect

## Sovelluksen ominaisuudet
* Käyttäjä voi luoda tunnuksen ja kirjautua sisään.
* Käyttäjä voi etsiä muiden tekemiä varauksia sekä luoda omia.
* Käyttäjä voi muokata ilmoituksiaan.
* Käyttäjä voi etsiä ilmoituksia nimellä.

## TO:DO
* Käyttäjä voi muokata profiiliaan
* Käyttäjä voi lisätä ilmoituksiinsa avainsanoja, kuvia sekä lisätietoja.
* Käyttäjä voi vastaanottaa ilmoituksia tietyistä varauksista.
* Käyttäjä voi etsiä ilmoituksia mm. ajan ja tunnisteiden perusteella.
* Sovelluksessa on tilastosivu, joka näyttää anonyymeja tilastoja sivuston käytöstä.
* Käyttäjä pystyy merkitsemään itsensä muiden varauksiin.
* Varauksissa on keskustelukenttä.

## Sovelluksen käyttäminen
1. Luo tietokanta
```
sqlite3 database.db < schema.sql
```

2. Käynnistä palvelin 
```
flask run
```