<html>
<head>

<style type="text/css">

body, html {
  background-color: #000000;
  margin:0;
  padding:0;
}


th {
  color: #1476C9;
  font-size:90%;
  border: none;
  padding: 0.2%; 
  font-weight: bold;
  text-align: center;
  padding-left: 3%;
}

img {

  width: 98%;
  height: 96%;
  padding-left: 1%; 
  padding-top: 1%; 

}

.dashboardcontainer {
  position: relative;
}


.table {
    border-collapse: collapse;
    border:1px solid #1B329E;
    width: 100%; 
    height:100%;
    
    
    font-family: "Helvetica Neue";
}

.accounttext {
  color: #FFFFFF;
  font-size:90%;
  border: none;
  text-align: center; 
  padding: 0.8%; 
  padding-left: 3%;
}


.heading {
    border-bottom: 1px solid #1B329E;
}



.accounttablecontainer {
  position: absolute;
  top: 13%;
  left: 7%;
  width: 33.7%; 
  height:70%;

}


.btcamount {
  position: absolute;
  top: 84%;
  left: 8%;
  width: 33.7%;
  color: #FFFFFF;
  font-size:99%;
  font-weight: bold;

}


.actionstablecontainer {
  position: absolute;
  top: 13%;
  left: 40.5%;
  width: 42%; 
  height:50%;

}

.actionrow{

  font-size:90%;
  border: none;
  text-align: center; 
  padding: 0.8%; 
  padding-left: 3%;


}

.row-buy{
  color:#00B7CF;
  font-size:90%;

}

.row-sell{
  color:#FF5615;
  font-size:90%;
}

.trendcontainer {
  position: absolute;
  top: 13%;
  left: 84%;
  width: 10%; 
  height:50%;

}


.trendtext {
  color: #FFFFFF;
  font-size:90%;
  border: none;
  text-align: center; 
  padding: 0.8%; 
}




</style>


</head>
<body>

<div class="dashboardcontainer">
<img src="dashboard.png"> 


	<div class="accounttablecontainer">

	<table class="table">
	<tbody>
	<tr class="heading">
		<th>Pair</th>
		<th>Amount</th>
		<th>In BTC</th>
	</tr>

<?php

//$fink=mysqli_connect("138.197.194.3","dev","5AKC08noMTwx9lG2","Fink");
$fink=mysqli_connect("localhost","root","Amm02o16!","Fink");
$edel=mysqli_connect("138.197.194.3","user","QkK9GTOQuia5DjzC","Edel");

// Check connection
if (mysqli_connect_errno())
{
echo "Failed to connect to MySQL: " . mysqli_connect_error();
}

$result = mysqli_query($fink,"SELECT * FROM Pairs WHERE HoldBTC > 0 ORDER BY HoldBTC DESC ");


while($row = mysqli_fetch_array($result))
{
echo "<tr>";
echo "<td class='accounttext'>" . $row['Pair'] . "</td>";
echo "<td class='accounttext'>" . $row['Hold'] . "</td>";
echo "<td class='accounttext'>" . $row['HoldBTC'] . "</td>";
echo "</tr>";
}


$result = mysqli_query($fink,"SELECT * FROM AccountBalance ORDER BY DateTime DESC LIMIT 1");
$row = mysqli_fetch_row($result);


echo "</tbody>";
echo "</table>";



?>


	</div>

	<div class="btcamount">
		<p class="BTC"> Total BTC Detected: <?php echo $row[1] . " / $" . $row[2] ?> </p> 
	</div>





<div class="actionstablecontainer">

	<table class="table">
	<tbody>
	<tr class="heading">
		<th>Pair</th>
		<th>Action</th>
		<th>In BTC</th>
		<th>Price</th>
		<th>Time</th>
	</tr>




<?php


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

echo "<td class='actionrow'>" . $row['Pair'] . "</td>";
echo "<td class='actionrow'>" . $row['Action'] . "</td>";
echo "<td class='actionrow'>" . $row['Price'] . "</td>";
echo "<td class='actionrow'>" . $ReturnBTC . "</td>";
echo "<td class='actionrow'>" . $row['ActionTime'] . "</td>";
echo "</tr>";
}


echo "</tbody>";
echo "</table>";


mysqli_close($fink);
?>


</div> 


<div class="trendcontainer">

	<table class="table">
	<tbody>
	<tr class="heading">
		<th>Active Pair</th>
	</tr>

    

<?php

// Check connection
if (mysqli_connect_errno())
{
echo "Failed to connect to MySQL: " . mysqli_connect_error();
}


$result = mysqli_query($edel,"SELECT Pair,Watch FROM Pair_List WHERE Watch=1;");


while($row = mysqli_fetch_array($result))
{
echo "<tr>";
echo "<td class='trendtext'>" . $row['Pair'] . "</td>";

echo "</tr>";
}
echo "</tbody>";
echo "</table>";

mysqli_close($edel);
?>

</div>


	
</div>

</body>
</html>
