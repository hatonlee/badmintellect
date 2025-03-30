# badmintellect

## Sovelluksen ominaisuudet
* Käyttäjä voi luoda tunnuksen, kirjautua sisään sekä muokata profiiliaan.
* Käyttäjä voi etsiä muiden tekemiä varauksia sekä luoda omia.
* Käyttäjä voi muokata ilmoituksiaan, lisätä niihin avainsanoja, kuvia sekä lisätietoja.
* Käyttäjä voi vastaanottaa ilmoituksia tietyistä varauksista.
* Käyttäjä voi etsiä ilmoituksia hakusanoilla ja eri ominaisuuksilla.
* Sovelluksessa on tilastosivu, joka näyttää anonyymeja tilastoja sivuston käytöstä.
* Käyttäjä pystyy merkitsemään itsensä muiden varauksiin.

## Sovelluksen käyttäminen
1. Luo tietokanta
`sqlite3 database.db < schema.sql`

2. Käynnistä palvelin
`flask run`