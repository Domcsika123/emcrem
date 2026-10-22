<?php
/**
 * Ajánlatkérő űrlap feldolgozása (PHP mail()).
 * A címzett és a feladó alább módosítható. A feladó domainje egyezzen a weboldaléval (SPF/DKIM).
 */
declare(strict_types=1);

const RECIPIENT = 'aed@emcrem.hu';
const SENDER    = 'noreply@emcremdefibrillator.hu';
const TOPICS    = [
    'aed'     => 'Automata defibrillátor (AED-3100)',
    'oktatas' => 'Munkahelyi elsősegély-oktatás',
    'extrak'  => 'Oktatás extrák',
    'szakmai' => 'Szakmai eszközök',
    'egyeb'   => 'Egyéb kérdés',
];

function redirect(string $to): void {
    header('Location: ' . $to, true, 303);
    exit;
}

function line(string $key, int $max = 200): string {
    $v = trim((string)($_POST[$key] ?? ''));
    $v = preg_replace('/[\r\n\t]+/', ' ', $v) ?? '';
    return mb_substr($v, 0, $max);
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    redirect('/ajanlatkeres/');
}

// Spamcsapda: a rejtett mezőt csak robotok töltik ki – nekik "sikert" mutatunk.
if (trim((string)($_POST['weboldal'] ?? '')) !== '') {
    redirect('/koszonjuk/');
}

$nev     = line('nev', 120);
$email   = line('email', 160);
$telefon = line('telefon', 40);
$ceg     = line('ceg', 160);
$letszam = line('letszam', 6);
$targy   = TOPICS[line('targy', 20)] ?? TOPICS['egyeb'];
$uzenet  = mb_substr(trim((string)($_POST['uzenet'] ?? '')), 0, 5000);
$consent = ($_POST['adatvedelem'] ?? '') === '1';

if ($nev === '' || !filter_var($email, FILTER_VALIDATE_EMAIL) || !$consent) {
    redirect('/ajanlatkeres/?hiba=adat#urlap');
}

$body = "Új ajánlatkérés érkezett az emcremdefibrillator.hu oldalról.\n\n"
      . "Téma:     {$targy}\n"
      . "Név:      {$nev}\n"
      . "E-mail:   {$email}\n"
      . "Telefon:  " . ($telefon ?: '–') . "\n"
      . "Cég:      " . ($ceg ?: '–') . "\n"
      . "Létszám:  " . ($letszam ?: '–') . "\n\n"
      . "Üzenet:\n" . ($uzenet ?: '–') . "\n\n"
      . "---\nAdatkezelési tájékoztató elfogadva: igen\n"
      . 'Időpont: ' . date('Y-m-d H:i') . "\n";

$subject = mb_encode_mimeheader("Ajánlatkérés: {$targy} – {$nev}", 'UTF-8', 'B');
$headers = implode("\r\n", [
    'From: ' . mb_encode_mimeheader('Emcrem weboldal', 'UTF-8', 'B') . ' <' . SENDER . '>',
    'Reply-To: ' . $email,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
]);

$ok = mail(RECIPIENT, $subject, $body, $headers, '-f' . SENDER);
redirect($ok ? '/koszonjuk/' : '/ajanlatkeres/?hiba=kuldes#urlap');
