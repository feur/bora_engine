<html>
<head>

<style type="text/css">

body {
  background-color: #000000;
}

table {
    border-collapse: collapse;
    border:1px solid #C0A002;
    width: 98%; 
    height: 90%; 
    
    font-family: "Helvetica Neue";
}

.heading {
    border-bottom: 1px solid #C0A002;
}

th {
  color: #1476C9;
  font-size:11pt;
  border: none;
  padding: 0.8%; 
}

td {
  color: #00B7CF;
  font-size:10pt;
  border: none;
  text-align: center; 
  padding: 0.3%; 
}


</style>

</head>
<body>


<table>
<tbody>
<tr class="heading">
	<th>Signal</th>
	<th>Pair</th>
	<th>Time</th>
</tr>

<?php
//$fink=mysqli_connect("138.197.194.3","dev","5AKC08noMTwx9lG2","Fink");
$fink=mysqli_connect("localhost","root","Amm02o16!","Fink");
//$edel=mysqli_connect("138.197.194.3","user","QkK9GTOQuia5DjzC","Edel");

// Check connection
if (mysqli_connect_errno())
{
echo "Failed to connect to MySQL: " . mysqli_connect_error();
}

$result = mysqli_query($fink,"select * from SignalLog order by Time desc limit 20;");

while($row = mysqli_fetch_array($result))
{
echo "<tr>";
echo "<td>" ;

if ($row['TradeSignal'] == 2) {
        echo "Buy";
} else {
        echo "Sell";
}

echo "</td>";
echo "<td>" . $row['Pair'] . "</td>";
echo "<td>" . $row['Time'] . "</td>";
echo "</tr>";
}
echo "</tbody>";
echo "</table>";


mysqli_close($fink);
?>



	
	
</body>
</html>
