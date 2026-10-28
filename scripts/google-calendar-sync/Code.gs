/** Synchronisation unidirectionnelle Sheets → agenda public AstroQuébec.
 * Activer le service avancé Google Calendar API avant utilisation.
 * Commencer par apercuSynchronisation(). Voir README.md.
 */
const SYNC = {
  calendarId: '8c93e58e81334542ce90c2bd39b7b800b716aa5aa01419c321a525c43078933a@group.calendar.google.com',
  timeZone: 'America/Toronto',
  idColumn: 'AstroQuébec ID',
  sources: [
    { id: '1ZV_rL7AEFmk_SseSW-qtcWb4o7Wp3w0xhE4CYCdjsnY', gid: 0, header: 1, kind: 'activity', label: 'Activités' },
    { id: '1RgMvotaWYA2v1OBbQIbUGdM1vXiWpkI0OZByAloRjyE', gid: 1960152508, header: 2, kind: 'seminar', label: 'UdeM' },
    { id: '1ZFOU0qNz010exBnI2UC_IALXu3Kdp9gDFC_SuSLUScs', gid: 0, header: 1, kind: 'seminar', label: 'McGill',
      time: '15:30–16:30', location: 'Bell Room (Room 103), Rutherford Building, 3600 University, McGill University' }
  ]
};

function apercuSynchronisation() { runSync_(true); }
function synchroniserCalendrier() { runSync_(false); }

function installerSynchronisationHoraire() {
  // N'effacer que les déclencheurs de cette fonction appartenant à ce compte.
  ScriptApp.getProjectTriggers().filter(t => t.getHandlerFunction() === 'synchroniserCalendrier')
    .forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('synchroniserCalendrier').timeBased().everyHours(1).create();
}

function runSync_(preview) {
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  const counts = { read: 0, created: 0, updated: 0, unchanged: 0, errors: 0 };
  try {
    // Vérifier l'accès à l'agenda avant d'ajouter des identifiants aux feuilles.
    if (!preview) Calendar.Calendars.get(SYNC.calendarId);
    SYNC.sources.forEach(source => {
      try {
        const sheet = SpreadsheetApp.openById(source.id).getSheets().find(s => s.getSheetId() === source.gid);
        if (!sheet) throw new Error('Onglet introuvable : ' + source.gid);
        const values = sheet.getDataRange().getDisplayValues();
        const headers = values[source.header - 1].map(clean_);
        let idCol = headers.indexOf(SYNC.idColumn);
        const seenIds = new Set();
        const hint = values.slice(0, source.header - 1).flat().join(' ').match(/\b[AH]?(20\d{2})\b/);
        for (let row = source.header; row < values.length; row++) {
          try {
            const record = readRecord_(source, headers, values[row], hint ? Number(hint[1]) : null);
            if (!record) continue;
            counts.read++;
            if (preview) {
              console.log(JSON.stringify({ source: source.label, row: row + 1, event: record }));
              continue;
            }
            if (idCol < 0) {
              idCol = headers.length;
              if (idCol >= sheet.getMaxColumns()) sheet.insertColumnAfter(sheet.getMaxColumns());
              sheet.getRange(source.header, idCol + 1).setValue(SYNC.idColumn);
              headers.push(SYNC.idColumn);
            }
            let uuid = clean_(values[row][idCol]);
            if (!uuid) {
              uuid = Utilities.getUuid();
              sheet.getRange(row + 1, idCol + 1).setValue(uuid);
              // Enregistrer l'identité avant de créer l'événement : une reprise ne crée pas de doublon.
              SpreadsheetApp.flush();
            }
            if (seenIds.has(uuid)) throw new Error('ID dupliqué dans cette feuille : vider l’ID de la ligne copiée puis relancer.');
            seenIds.add(uuid);
            const key = source.id + ':' + source.gid + ':' + uuid;
            const eventId = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, key)
              .map(byte => ('0' + ((byte + 256) % 256).toString(16)).slice(-2)).join('');
            const resource = Object.assign({}, record, {
              extendedProperties: { private: { managedBy: 'astroquebec-sheets-v1', sourceKey: key } }
            });
            let existing;
            try { existing = Calendar.Events.get(SYNC.calendarId, eventId); }
            catch (error) {
              if (!/\b404\b|not found/i.test(String(error))) throw error;
            }
            if (existing) {
              if (existing.status === 'cancelled') throw new Error('Événement supprimé dans Google Agenda; rétablir manuellement ou vider son ID dans Sheets pour le recréer.');
              if (!existing.extendedProperties || !existing.extendedProperties.private || existing.extendedProperties.private.sourceKey !== key)
                throw new Error('Identité déjà utilisée : vérifier la colonne ' + SYNC.idColumn);
              if (sameEvent_(existing, resource)) { counts.unchanged++; continue; }
              Calendar.Events.patch(resource, SYNC.calendarId, eventId, { sendUpdates: 'none' });
              counts.updated++;
            } else {
              Calendar.Events.insert(Object.assign({ id: eventId }, resource), SYNC.calendarId, { sendUpdates: 'none' });
              counts.created++;
            }
          } catch (error) {
            counts.errors++;
            console.error(source.label + ', ligne ' + (row + 1) + ' : ' + error.message);
          }
        }
      } catch (error) {
        counts.errors++;
        console.error(source.label + ' : ' + error.message);
      }
    });
    console.log((preview ? 'APERÇU : ' : 'SYNCHRONISATION : ') + JSON.stringify(counts));
    if (counts.errors) throw new Error(counts.errors + ' erreur(s). Voir le journal; les autres lignes ont été traitées.');
  } finally { lock.releaseLock(); }
}

function clean_(value) { return String(value == null ? '' : value).replace(/\s+/g, ' ').trim(); }
function normalize_(value) { return clean_(value).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase(); }

function readRecord_(source, headers, values, yearHint) {
  // En-têtes répétés dans le fichier UdeM : prendre la dernière valeur non vide.
  function field(names) {
    let result = '';
    headers.forEach((header, index) => {
      if (names.includes(normalize_(header)) && clean_(values[index])) result = clean_(values[index]);
    });
    return result;
  }
  const name = source.kind === 'activity' ? field(["nom de l'activite"]) : field(['speaker', 'nom']);
  const date = field(['date']);
  if (!name || !date || /no seminar|winter break|vacances|no event|no talk|hold this spot/i.test(name)) return null;
  const ymd = dateParts_(date, yearHint);
  const rawTime = field(['heure', 'time']) || source.time || '';
  const location = field(['emplacement', 'local', 'location']) || source.location || '';
  const title = field(['titre', 'title']);
  const affiliation = field(['institution', 'affiliation']);
  const abstract = field(['resume', 'abstract']);
  // Liste explicite de champs publics. Ne pas exporter les courriels, notes, finances ou liens Zoom.
  const description = [source.kind === 'seminar' ? title : '', affiliation, abstract].filter(Boolean).join('\n\n');
  const record = { summary: source.kind === 'seminar' ? 'Séminaire — ' + name : name, location, description };
  if (/toute la journee|all day/i.test(normalize_(rawTime))) {
    const next = new Date(Date.UTC(ymd.year, ymd.month - 1, ymd.day + 1));
    record.start = { date: ymd.text };
    record.end = { date: next.toISOString().slice(0, 10) };
  } else {
    const range = timeRange_(rawTime);
    const stamp = minutes => ymd.text + ' ' + String(Math.floor(minutes / 60)).padStart(2, '0') + ':' + String(minutes % 60).padStart(2, '0');
    const start = Utilities.parseDate(stamp(range[0]), SYNC.timeZone, 'yyyy-MM-dd HH:mm');
    const end = Utilities.parseDate(stamp(range[1]), SYNC.timeZone, 'yyyy-MM-dd HH:mm');
    record.start = { dateTime: start.toISOString(), timeZone: SYNC.timeZone };
    record.end = { dateTime: end.toISOString(), timeZone: SYNC.timeZone };
  }
  return record;
}

function dateParts_(raw, yearHint) {
  const text = normalize_(raw).replace(/,/g, '');
  const months = { janvier:1,jan:1,january:1,fevrier:2,feb:2,february:2,mars:3,mar:3,march:3,avril:4,apr:4,april:4,mai:5,may:5,juin:6,jun:6,june:6,juillet:7,jul:7,july:7,aout:8,aug:8,august:8,septembre:9,sep:9,sept:9,september:9,octobre:10,oct:10,october:10,novembre:11,nov:11,november:11,decembre:12,dec:12,december:12 };
  let year, month, day;
  let match = text.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/);
  if (match) { year=Number(match[1]);month=Number(match[2]);day=Number(match[3]); }
  else {
    match = text.match(/^(\d{1,2})[\s-]+([a-z]+)(?:[\s-]+(\d{4}))?$/);
    if (!match) throw new Error('Date non reconnue : ' + raw);
    day=Number(match[1]);month=months[match[2]];year=match[3]?Number(match[3]):yearHint;
  }
  if (!year || !month || !day) throw new Error('Date ou année manquante : ' + raw);
  const check = new Date(Date.UTC(year, month-1, day));
  if (check.getUTCFullYear()!==year || check.getUTCMonth()!==month-1 || check.getUTCDate()!==day) throw new Error('Date invalide : ' + raw);
  return { year,month,day,text:check.toISOString().slice(0,10) };
}

function timeRange_(raw) {
  const match = normalize_(raw).match(/^(\d{1,2})(?:[h:](\d{2}))?\s*(?:a|to|–|—|-)\s*(\d{1,2})(?:[h:](\d{2}))?$/);
  if (!match) throw new Error('Horaire manquant ou non reconnu : ' + raw);
  const sh=Number(match[1]),sm=Number(match[2]||0),eh=Number(match[3]),em=Number(match[4]||0);
  if (sh>23 || eh>23 || sm>59 || em>59 || eh*60+em<=sh*60+sm) throw new Error('Horaire invalide : ' + raw);
  return [sh*60+sm,eh*60+em];
}

function sameEvent_(event, record) {
  function time(value) { return value.date || new Date(value.dateTime).toISOString(); }
  return (event.summary||'')===record.summary && (event.location||'')===record.location &&
    (event.description||'')===record.description && time(event.start)===time(record.start) && time(event.end)===time(record.end);
}
