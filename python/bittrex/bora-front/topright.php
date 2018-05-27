<html>
<head>

<style type="text/css">

</style>


</head>
<body>


<?php
$con=mysqli_connect("138.197.194.3","dev","5AKC08noMTwx9lG2","Bora_Test");
// Check connection
if (mysqli_connect_errno())
{
echo "Failed to connect to MySQL: " . mysqli_connect_error();
}

$result = mysqli_query($con,"select * from SignalLog order by Time desc limit 10;");

echo "<table border='1'>
<tr>
<th>TradeSignal</th>
<th>Pair</th>
<th>Trend</th>
<th>Time</th>
</tr>";

while($row = mysqli_fetch_array($result))
{
echo "<tr>";
echo "<td>" . $row['Pair'] . "</td>";
echo "<td>" . $row['TradeSignal'] . "</td>";
echo "<td>" .  "</td>";
echo "<td>" . $row['Time'] . "</td>";
echo "</tr>";
}
echo "</table>";


mysqli_close($con);
?>



	
	
</body>
</html>
