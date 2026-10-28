# Google Sheets → agenda AstroQuébec

Le fichier `Code.gs` est un projet Google Apps Script autonome pour les trois sources fournies. Les tests locaux couvrent l’import des données, les mises à jour et l’absence de doublons. L’installation et les autorisations s’effectuent dans le compte Google qui gère l’agenda.

## Sources configurées

| Source | Onglet (`gid`) | Traitement |
| --- | --- | --- |
| Activités — `1ZV_rL7AEFmk_SseSW-qtcWb4o7Wp3w0xhE4CYCdjsnY` | 0 | Date, Heure, Emplacement, Nom de l’activité; journées entières |
| UdeM — `1RgMvotaWYA2v1OBbQIbUGdM1vXiWpkI0OZByAloRjyE` | 1960152508 | Deuxième ligne comme en-tête, année tirée de `A2026`, horaires et locaux explicites |
| McGill — `1ZFOU0qNz010exBnI2UC_IALXu3Kdp9gDFC_SuSLUScs` | 0 | Date, Speaker, Affiliation, Title, Abstract; horaire et lieu configurés dans le script |

**Horaire et lieu confirmés :** McGill, 15 h 30–16 h 30, Bell Room (Room 103), Rutherford Building, 3600 University. Ces valeurs sont configurées dans le script, car ce fichier ne contient pas ces champs. Fuseau : `America/Toronto` (changements d’heure compris).

Les quatre journées de la rencontre annuelle sont importées comme quatre événements sur une journée entière. Les lignes sans personne présentatrice ou sans activité, les vacances et les réservations « Hold this spot » sont ignorées. Un séminaire avec une personne mais sans titre est conservé.

## Installation

1. Avec un compte pouvant **modifier les trois Sheets et l’agenda cible**, ouvrir <https://script.google.com/> et créer un projet.
2. Remplacer le contenu de `Code.gs` par celui fourni ici.
3. Dans **Paramètres du projet**, choisir le fuseau `America/Toronto`.
4. À gauche, **Services → + → Google Calendar API → Ajouter**. Avec un projet Google Cloud personnalisé, activer également Google Calendar API dans ce projet.
5. Exécuter **`apercuSynchronisation`** et autoriser l’accès demandé. Cette fonction lit les sources et affiche les événements proposés dans le journal; elle ne modifie ni les fichiers ni l’agenda.
6. Vérifier les dates, lieux, horaires et descriptions publiques dans le journal.
7. Exécuter **`synchroniserCalendrier`** pour importer les événements. Cette fonction ajoute une colonne **AstroQuébec ID** à la fin de chaque onglet et y enregistre des identifiants stables. Ne pas effacer ou recopier ces identifiants. Lors d’un tri, inclure cette colonne dans le tri; une nouvelle ligne doit avoir un ID vide.
8. Vérifier le résultat dans Google Agenda, puis exécuter **`installerSynchronisationHoraire`** une fois. Le déclencheur s’exécute avec les droits du compte qui l’installe. L’agenda intégré au site affichera ensuite les événements.

## Mise à jour et limites

- Les modifications de titre, date, horaire, lieu et résumé d’une ligne mettent à jour son événement existant. Un ID Google déterministe évite de recréer l’événement si une exécution est interrompue.
- Les événements créés manuellement dans l’agenda ne sont pas modifiés. Les événements existants importés par un autre outil ne sont pas automatiquement rapprochés : vérifier les doublons avant le premier import.
- Retirer ou vider une ligne **ne supprime pas** l’événement correspondant. Pour une annulation, retirer la ligne de la source puis supprimer l’événement dans l’agenda. Une suppression dans l’agenda seule est signalée tant que la ligne reste présente.
- Les changements faits directement dans Google Agenda peuvent être remplacés lors de la prochaine synchronisation : les Sheets sont la source des champs synchronisés.
- Seuls les champs publics nommés dans le script sont transférés. Courriels, hôtes, notes internes, finances et liens Zoom sont exclus.
- Un horaire invalide est signalé sans inventer une heure. Les erreurs sont consignées par source et numéro de ligne; les autres lignes continuent à être traitées.
- Chaque onglet configuré est lu en entier, y compris les événements passés. Les autres onglets ne sont pas importés.
- Aucune invitation ni notification aux participants n’est envoyée.

Références : [service avancé Calendar](https://developers.google.com/apps-script/advanced/calendar), [activation des services avancés](https://developers.google.com/apps-script/guides/services/advanced), [identifiants d’événements](https://developers.google.com/workspace/calendar/api/v3/reference/events/insert), [déclencheurs installables](https://developers.google.com/apps-script/guides/triggers/installable).
