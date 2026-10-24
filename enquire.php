<?php
// Career Hub Nagaland enquiry handler.
// Saves each enquiry to a private CSV outside the web root and emails a summary.
declare(strict_types=1);
date_default_timezone_set('Asia/Kolkata');

const ENQUIRY_TO = 'emmanuelyanthan@rediffmail.com'; // change to hello@careerhubnagaland.in once that mailbox exists
const THANKS_URL = '/enquire/thanks/';

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Location: /enquire/', true, 303);
    exit;
}

function field(string $key, int $max = 200): string {
    $v = trim((string)($_POST[$key] ?? ''));
    $v = preg_replace('/[\r\n\t]+/', ' ', $v) ?? '';
    return mb_substr($v, 0, $max);
}

function fail(string $message): void {
    http_response_code(400);
    header('Content-Type: text/html; charset=utf-8');
    $m = htmlspecialchars($message, ENT_QUOTES);
    echo "<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
       . "<title>Please check your enquiry</title><link rel=stylesheet href='/assets/site.css'>"
       . "<main class='wrap section prose'><h1>Please check your enquiry</h1><p>$m</p>"
       . "<p><a class='btn btn-primary' href='javascript:history.back()'>Go back to the form</a></p>"
       . "<p>Or message us on WhatsApp: <a href='https://wa.me/919366092897'>+91 93660 92897</a></p></main>";
    exit;
}

// Bots: hidden field filled, or submitted faster than a person could
if (field('website') !== '') { header('Location: ' . THANKS_URL, true, 303); exit; }
$t = (int)($_POST['t'] ?? 0);
if ($t > 0 && (time() * 1000 - $t) < 3000) { header('Location: ' . THANKS_URL, true, 303); exit; }

$who = field('who', 20);
if (!in_array($who, ['parent', 'student18', 'graduate', 'school'], true)) fail('Please choose who the enquiry is for.');
$name = field('name', 120);
if ($name === '') fail('Please enter your name.');
$phone = field('phone', 20);
if (strlen(preg_replace('/\D/', '', $phone) ?? '') < 10) fail('Please enter a WhatsApp number with at least 10 digits.');
if (field('consent', 5) !== 'yes') fail('Please tick the consent box so we can reply to you.');

$email = field('email', 160);
if ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL)) fail('Please check the email address, or leave it empty.');

$row = [
    'received'    => date('c'),
    'who'         => $who,
    'name'        => $name,
    'phone'       => $phone,
    'email'       => $email,
    'service'     => field('service', 40),
    'class'       => field('class', 20),
    'board'       => field('board', 20),
    'school_name' => field('school_name', 160),
    'role'        => field('role', 80),
    'students'    => field('students', 10),
    'concern'     => field('concern', 80),
    'format'      => field('format', 40),
    'when'        => field('when', 40),
    'source'      => field('source', 40),
    'message'     => field('message', 1000),
    'consent'     => 'yes',
    'whatsapp_optin' => field('optin', 5) === 'yes' ? 'yes' : 'no',
];

// Store outside public_html when possible; otherwise in a locked folder inside it.
$dir = dirname(__DIR__) . '/chn-enquiries';
if (!is_dir($dir) && !@mkdir($dir, 0750, true)) {
    $dir = __DIR__ . '/_data';
    if (!is_dir($dir)) { @mkdir($dir, 0750, true); }
    @file_put_contents($dir . '/.htaccess', "Require all denied\n");
}
$file = $dir . '/enquiries.csv';
$new = !file_exists($file);
if ($fh = @fopen($file, 'a')) {
    if (flock($fh, LOCK_EX)) {
        if ($new) fputcsv($fh, array_keys($row));
        // Neutralise spreadsheet formula injection
        fputcsv($fh, array_map(fn($v) => preg_match('/^[=+\-@]/', $v) ? "'" . $v : $v, $row));
        flock($fh, LOCK_UN);
    }
    fclose($fh);
}

$lines = [];
foreach ($row as $k => $v) { if ($v !== '') $lines[] = str_pad($k, 15) . ': ' . $v; }
$subject = 'New enquiry: ' . $row['service'] . ' (' . $who . ')';
$host = preg_replace('/[^a-z0-9.\-]/i', '', $_SERVER['HTTP_HOST'] ?? 'careerhubnagaland.in');
$headers = 'From: Career Hub Nagaland website <noreply@' . $host . ">\r\n"
         . 'Content-Type: text/plain; charset=utf-8';
if ($email !== '') $headers .= "\r\nReply-To: " . $email;
@mail(ENQUIRY_TO, '=?UTF-8?B?' . base64_encode($subject) . '?=', implode("\n", $lines), $headers);

header('Location: ' . THANKS_URL, true, 303);
