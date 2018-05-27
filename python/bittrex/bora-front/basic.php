<?php
$con=mysqli_connect("138.197.194.3","dev","5AKC08noMTwx9lG2","Bora_Test");
// Check connection
if (mysqli_connect_errno())
{
echo "Failed to connect to MySQL: " . mysqli_connect_error();
}

$result = mysqli_query($con,"SELECT * FROM Pairs ORDER BY Rating DESC");

echo "<table border='1'>
<tr>
<th>Pair</th>
<th>Rating</th>
<th>TradeSignal</th>
<th>PID</th>
<th>Bought</th>
<th>Hold</th>
<th>HoldBTC<th>
</tr>";

while($row = mysqli_fetch_array($result))
{
echo "<tr>";
echo "<td>" . $row['Pair'] . "</td>";
echo "<td>" . $row['Rating'] . "</td>";
echo "<td>" . $row['TradeSignal'] . "</td>";
echo "<td>" . $row['PID'] . "</td>";
echo "<td>" . $row['Bought'] . "</td>";
echo "<td>" . $row['Hold'] . "</td>";
echo "<td>" . $row['HoldBTC'] . "</td>";
echo "</tr>";
}
echo "</table>";








mysqli_close($con);
?>
