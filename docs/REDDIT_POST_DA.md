# Reddit-udkast

Del først med et link til den gennemgåede version, når dens releasebetingelser er
opfyldt. Dette er et udkast, ikke et publiceret opslag.

## Titel

Jeg har bygget et åbent værktøj til at gennemgå leasingtilbud med en AI-assistent

## Opslag

Et leasingtilbud kan se billigt ud på månedsydelsen, mens førstegangsydelse,
gebyrer, løbetid og kilometer gør sammenligningen mindre enkel.

Jeg har derfor bygget GLASSBOX-AUTO: et åbent Python-værktøj, som en AI-assistent
kan bruge til at gennemgå konkrete privatleasingtilbud. Assistenten samler
oplysningerne og viser dem til dig først. Når du har bekræftet dem, beregner
værktøjet udgiften og peger på manglende vilkår.

Det viser løbende betaling, betaling over perioden og gennemsnit pr. måned hver
for sig. Depositum og kilometer-scenarier behandles særskilt. Manglende gebyrer
bliver ikke bare til 0 kr.

Betaen er et omkostningstjek af de tilbud, du giver den. Den vurderer ikke, hvilken
bil der er bedst for dig, og bekræfter ikke, at annoncen stadig gælder. Din
assistent skal kunne køre Python. Kan den kun læse links, hjælper den med
inputtene og skal tydeligt sige, at beregningen ikke er kørt.

Kode, metode, test og dansk startvejledning:
https://github.com/BBSupreme/GLASSBOX-AUTO

Jeg vil især gerne have feedback på uklare forklaringer og tilbud, hvor
betalingsvilkårene ikke passer til modellen. En lille fiktiv gengivelse er nok til
at undersøge en fejl. Del ikke personlige tilbud, kundeoplysninger eller din fulde
økonomi i en offentlig issue.
