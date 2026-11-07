# Tjek et leasingtilbud med din AI-assistent

GLASSBOX-AUTO beregner udgiften i et konkret privatleasingtilbud og viser, hvilke
oplysninger der mangler. Du kan gennemgå ét tilbud eller stille flere tilbud ved
siden af hinanden.

**Det er en beta til omkostningstjek.** Den søger ikke automatisk hele markedet,
vurderer ikke hvilken bil der passer bedst til familien og bekræfter ikke, at en
annonce stadig gælder.

## Kopiér dette til din AI-assistent

```text
Brug GLASSBOX-AUTO til at gennemgå mine privatleasingtilbud:
https://github.com/BBSupreme/GLASSBOX-AUTO

Læs AGENTS.md og docs/AI_QUICKSTART.md fra samme fastlåste commit.
Undersøg først, om du faktisk kan hente filerne og køre Python-programmet.
Hvis du ikke kan køre det, skal du skrive UNEXECUTED og hjælpe mig med
at gøre oplysningerne klar uden at opfinde et motorresultat.

Bed om mine tilbud, forventede årlige kilometer og eventuelle budgetgrænser.
Bevar manglende oplysninger som ukendte. Vis de samlede input, kilder,
datoer og antagelser, og bed om min bekræftelse før beregningen.

Når jeg har bekræftet, skal du køre programmet og vise løbende betaling,
betaling over hele perioden, gennemsnit pr. måned, indledende betalinger
uden de løbende ydelser og manglende vilkår. Hold depositum og eventuelle
kilometer-scenarier tydeligt adskilt. Vis den faktiske kommando, version
samt input- og resultatfingeraftryk. Forklar beregningens afgrænsning.
```

Et GitHub-link giver ikke i sig selv en chatbot mulighed for at køre kode. Hvis
din assistent svarer **UNEXECUTED**, kan den stadig læse tilbuddet og samle
spørgsmål til forhandleren. Du kan også
[køre Python-programmet selv](AI_QUICKSTART.md#try-the-synthetic-example).

## Det skal du have klar

- Tilbuddet som tekst, link eller relevante uddrag. Fjern navn, adresse,
  kundenummer og andre private oplysninger.
- Et privat operationelt leasingtilbud med forbrugerpriser inklusive moms.
  Erhvervspriser eksklusive moms, finansiel leasing/flexleasing og aftaler med
  restværdiforpligtelser ligger uden for denne beta.
- Præcis bilvariant, løbetid, antal betalinger og kilometer pr. år.
- Førstegangsydelse, månedsydelse, obligatoriske gebyrer og eventuelt depositum.
  Gem formuleringen om, hvad der er inkluderet, og hvornår gebyrerne betales.
- Datoen du fandt tilbuddet og eventuel udløbsdato.
- Dit kørselsbehov og eventuelle budgetgrænser. Angiv, om den månedlige grænse
  gælder leasing alene eller leasing plus ekstra forsikringsudgift.

Du behøver ikke kende alle beløb. Assistenten skal vise manglerne og deres
betydning. Et ukendt gebyr må ikke erstattes af 0 kr.

## Sådan læser du svaret

| Felt | Betydning |
|---|---|
| Løbende betaling | Den sædvanlige månedsregning på den angivne prisbasis |
| Betaling over hele perioden | Ikke-refunderbar startbetaling, alle månedlige betalinger og yderligere obligatoriske gebyrer |
| Gennemsnit pr. måned | Periodens betaling fordelt over løbetiden; ikke din månedsregning |
| Indledende ikke-månedlige betalinger | Startbetaling, gebyrer med kendt starttidspunkt og depositum; første løbende månedsydelse er ikke med |
| Kilometer-scenarie | En oplyst ekstra-km-pris anvendt på dit kørselsbehov; kontraktens accept af kørslen skal afklares |
| Manglende vilkår og kildestatus | Hvilke konklusioner der endnu ikke kan drages |

**Læg første månedsydelse til separat, når du planlægger kontantbehov ved start.**
Grænsen `max_initial_non_monthly_dkk` omfatter kun betalinger uden for de løbende
ydelser. Afklar også, hvornår forsikringen betales. Et refunderbart depositum
vises som bundet likviditet; tilbagebetaling
afhænger af kontrakten og afleveringen.

Et fiktivt tilbud med 10.000 kr. i ikke-refunderbar startbetaling, 36 betalinger
à 3.000 kr. og 2.000 kr. i ekstra obligatoriske gebyrer koster 120.000 kr. over
perioden, cirka 3.333 kr. pr. måned. Den løbende ydelse er stadig 3.000 kr.
Eksemplet er en illustration og ikke et aktuelt tilbud.

Forsikring, strøm/brændstof, særskilte afgifter, dæk, skader og andre
omkostninger kan ligge udenfor. Hold løbetid og kilometer synlige ved en
sammenligning. Kildelinks og en vellykket beregning beviser ikke, at et tilbud er
korrekt eller kan bestilles.

## Feedback og mere læsning

Del helst en lille **fiktiv gengivelse** af en fejl i en
[GitHub-issue](https://github.com/BBSupreme/GLASSBOX-AUTO/issues/new/choose).
Angiv version/commit, kommando, faktisk resultat og forventning. Del ikke dit
originale personlige tilbud eller din fulde husstandsprofil.

Se [inputkontrakten](OFFER_CHECK_CONTRACT_v1.md),
[den tekniske vejledning](AI_QUICKSTART.md) og [metoden](METHOD.md).
