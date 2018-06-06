<html>
<head>

<style type="text/css">

body {
  background-color: #000000;
}

table {
    border-collapse: collapse;
    border:1px solid #C0A002;
    width: 97%; 
    height: 100%; 
    
    font-family: "Helvetica Neue";
}

.heading {
    border-bottom: 1px solid #C0A002;
}

th {
  color: #1476C9;
  font-size:11pt;
  border: none;
  padding: 0.2%; 
}



td {
  font-size:10pt;
  border: none;
  text-align: center; 
  padding: 0.8%; 
}


.row-buy{
  color:#00B7CF;
}

.row-sell{
  color:#FF5615;
}


</style>


</head>
<body>

<table id="action-table">

<tbody>
<tr class="heading">
	<th>Pair</th>
	<th>Action</th>
	<th>Amount</th>
	<th>Price</th>
	<th>In BTC</th>
	<th>Time</th>
</tr>




<?php

$fink=mysqli_connect("138.197.194.3","dev","5AKC08noMTwx9lG2","Fink");
//$fink=mysqli_connect("localhost","root","Amm02o16!","Fink");
//$edel=mysqli_connect("138.197.194.3","user","QkK9GTOQuia5DjzC","Edel");

// Check connection
if (mysqli_connect_errno())
{
echo "Failed to connect to MySQL: " . mysqli_connect_error();
}

$result = mysqli_query($fink,"select * from AccountHistory order by ActionTime desc limit 8");



while($row = mysqli_fetch_array($result))
{

$ReturnBTC = $row['Amount'] * $row['Price'];

if ($row['Action'] == "Buy")
{
  $rowClass = "row-buy";
}
else
{
  $rowClass = "row-sell";
}

echo "<tr class='".$rowClass."'>";

echo "<td>" . $row['Pair'] . "</td>";
echo "<td>" . $row['Action'] . "</td>";
echo "<td>" . $row['Amount'] . "</td>";
echo "<td>" . $row['Price'] . "</td>";
echo "<td>" . $ReturnBTC . "</td>";
echo "<td>" . $row['ActionTime'] . "</td>";
echo "</tr>";
}

echo "</tbody>";


mysqli_close($fink);
?>



	
	
</body>
</html>
