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

$result = mysqli_query($con,"select * from AccountHistory order by ActionTime desc limit 10");

echo "<table border='1'>
<tr>
<th>Pair</th>
<th>Action</th>
<th>Amount</th>
<th>Price</th>
<th>BTC</th>
<th>Time</th>
</tr>";

while($row = mysqli_fetch_array($result))
{

$ReturnBTC = $row['Amount'] * $row['Price'];

echo "<tr>";
echo "<td>" . $row['Pair'] . "</td>";
echo "<td>" . $row['Action'] . "</td>";
echo "<td>" . $row['Amount'] . "</td>";
echo "<td>" . $row['Price'] . "</td>";
echo "<td>" . $ReturnBTC . "</td>";
echo "<td>" . $row['ActionTime'] . "</td>";
echo "</tr>";
}


mysqli_close($con);
?>



	
	
</body>
</html>
