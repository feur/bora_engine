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

$result = mysqli_query($con,"SELECT * FROM Pairs WHERE HoldBTC > 0 ORDER BY HoldBTC DESC ");

echo "<table border='1'>
<tr>
<th>Pair</th>
<th>Amount</th>
<th>In BTC</th>
<th>Trend</th>
</tr>";

while($row = mysqli_fetch_array($result))
{
echo "<tr>";
echo "<td>" . $row['Pair'] . "</td>";
echo "<td>" . $row['Hold'] . "</td>";
echo "<td>" . $row['HoldBTC'] . "</td>";

echo "<td>";

if ($row['Watch'] == 1) {
	echo "UP"; 
}
else {
	echo "Down";
} 

echo "</td>";

echo "</tr>";
}


$result = mysqli_query($con,"SELECT * FROM AccountBalance ORDER BY DateTime DESC LIMIT 1");
$row = mysqli_fetch_row($result);


echo "<tr>";
echo "<td> Total BTC Detected: </td>";
echo "<td>" . $row[1] . "</td>";
echo "<td> $" . $row[2] . "</td>";
echo "</tr>";



echo "</table>";








mysqli_close($con);
?>



	
	
</body>
</html>
