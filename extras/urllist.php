<?php
//
// This is a simple PHP script to display the URLs grabbed by urlgrab.py.
// If you use it, remember to customize the database connection step.
//
?>

<html>
  <head>
    <title>&lt;channel/bot name&gt; URLs</title>
  </head>
  <body>
    <h1>&lt;channel/bot name&gt; URLs</h1>
<?php
// Only get stuff for a week.
$oldest = date("Y-m-d", time()-604800);

// Change connection to use appropriate username and password.
$dbconn = pg_connect("dbname=moobot");

$result = pg_exec($dbconn, "SELECT nick, string, time, url_id FROM url WHERE time > '$oldest' ORDER BY time DESC");
if (pg_numrows($result) > 0) {
  print "    <table>\n";
  for ($i = 0; $i < pg_numrows($result); $i++) {
    $arr = pg_fetch_array($result, $i);

    // What URLs shall we skip?
    if (preg_match("{freshmeat.net/admin}i", $arr[string])) {
      continue;
    }

    $prefix = "";

    // It matches a lot of types of URLs, believe me.
    if (! preg_match_all("{([a-z][a-z0-9+-]*:(//(((([-a-z0-9_.!~*\'();:&=+$\,]|%[0-9a-f][0-9a-f])*@)?((([a-z0-9]([a-z0-9-]*[a-z0-9])?)\.)*([a-z]([a-z0-9-]*[a-z0-9])?)\.?|[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)(:[0-9]+)?)|([-a-z0-9_.!~*\'()$\,;:@&=+]|%[0-9a-f][0-9a-f])+)(/([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*(;([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*)*(/([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*(;([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*)*)*)?(\?([-a-z0-9_.!~*\'();/?:@&=+$\,]|%[0-9a-f][0-9a-f])*)?|([-a-z0-9_.!~*\'();?:@&=+$\,]|%[0-9a-f][0-9a-f])([-a-z0-9_.!~*\'();/?:@&=+$\,]|%[0-9a-f][0-9a-f])*)(#([-a-z0-9_.!~*\'();/?:@&=+$\,]|%[0-9a-f][0-9a-f])*)?)}i", $arr[string], $matches)) {
      preg_match_all("{(www.(([a-z0-9]([a-z0-9-]*[a-z0-9])?)\.)*([a-z]([a-z0-9-]*[a-z0-9])?)\.?(:[0-9]+)?(/([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*(;([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*)*(/([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*(;([-a-z0-9_.!~*\'():@&=+$\,]|%[0-9a-f][0-9a-f])*)*)*)?(\?([-a-z0-9_.!~*\'();/?:@&=+$\,]|%[0-9a-f][0-9a-f])*)?(#([-a-z0-9_.!~*\'();/?:@&=+$\,]|%[0-9a-f][0-9a-f])*)?)}i", $arr[string], $matches);
      $prefix = "http://";
    }

    $fstring = htmlspecialchars($arr[string]);
    for ($j = 0; $j < count($matches[0]); $j++) {
      $url = $matches[0][$j];
      $url = preg_replace("/[.,?!)]$/", "", $url);
      $encurl = htmlspecialchars($url);
      $url = $prefix . $url;
      $fstring = preg_replace ("{".preg_quote($encurl)."}", 
			       "<a href=\"$url\"><tt>$encurl</tt></a>",
			       $fstring);
    }
    print "      <tr>\n";
    print "        <!-- $arr[url_id]; $arr[time] -->\n";
    print "        <td align=\"right\"><i>$arr[nick]</i></td>\n";
    print "        <td>$fstring</td>\n";
    print "      </tr>\n";
  }
  echo "    </table>\n";
} else {
?>
    <p>No results for this time period.</p> 
<?php
}
?>
    <br>

    <a href="../">Back to main page.</a><br>
  </body>
</html>
