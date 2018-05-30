<html>
<head>

<style type="text/css">

</style>


</head>
<body>


<?php
//$con=mysqli_connect("138.197.194.3","dev","5AKC08noMTwx9lG2","Bora_Test");
$con=mysqli_connect("localhost","root","Amm02o16!","Fink");
$edel=mysqli_connect("138.197.194.3","user","QkK9GTOQuia5DjzC","Edel");


// Check connection
if (mysqli_connect_errno())
{
echo "Failed to connect to MySQL: " . mysqli_connect_error();
}

$result = mysqli_query($con,"select * from SignalLog order by Time desc limit 10;");

echo "<table border='1'>
<tr>
<th>Signal</th>
<th>Pair</th>
<th>Time</th>
</tr>";

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
echo "</table>";




$result = mysqli_query($edel,"SELECT Pair,Watch FROM Pair_List WHERE Watch=1;");

echo "<table border='1'>
<tr>
<th>Pair</th>
<th>Trend</th>
</tr>";

while($row = mysqli_fetch_array($result))
{
echo "<tr>";
echo "<td>" . $row['Pair'] . "</td>";
echo "<td>" ;

if ($row['Watch'] == 1) {
        echo "UP";
} else {
        echo "Down";
}

echo "</td>";
echo "</tr>";
}
echo "</table>";







mysqli_close($con);
?>



        
        
</body>
</html>

