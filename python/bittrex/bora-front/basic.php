<?php
$page = $_SERVER['PHP_SELF'];
$sec = "10";
?>
<html>
    <head>

    <meta http-equiv="refresh" content="<?php echo $sec?>;URL='<?php echo $page?>'">

    </head>

    <body>

   <?php
$con=mysqli_connect("localhost","root","asdfqwer1","Bora");
// Check connection
if (mysqli_connect_errno())
{
echo "Failed to connect to MySQL: " . mysqli_connect_error();
}

$result = mysqli_query($con,"SELECT * FROM Pairs");

echo "<table border='1'>
<tr>
<th>Pair</th>
<th>Rating</th>
<th>TradeSignal</th>
<th>PID</th>
<th>Bought</th>
<th>Hold</th>
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
echo "</tr>";
}
echo "</table>";

mysqli_close($con);


?>
    </body>
</html>




