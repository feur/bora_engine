<html>
<head>

<style type="text/css">

body, html {
  background-color: #FFFFFF;
  margin:0;
  padding:0;
}


th {
  color: #1476C9;
  font-size:80%;
  border: none;
  padding: 0.5%; 
  font-weight: bold;
  text-align: center;
  padding-left: 3%;
}

img {

  
  padding-left: 1%; 
  padding-top: 1%; 
  width: 100%; 
  height:100%;

}

.dashboardcontainer {
  position: relative;
  width: 85%;
  height: 78%;
  
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
  top: 14%;
  left: 6.5%;
  width: 20%; 
  height:85%;

}

.btcamount {
  position: absolute;
  top: 5%;
  left: 6.5%;
  color: #1476C9;
  font-size: 80%;
  font-weight: bold;

}

.actionstablecontainer {
  position: absolute;
  top: 14%;
  left: 27%;
  width: 55%; 
  height:54%;

}

.SignalHistoryContainer {

  position: absolute;
  top: 2%;
  left: 87%;
  width: 10%; 
  height:77%;


}

.actionrow{

  font-size:80%;
  border: none;
  text-align: center; 
  font-weight: bold;
  padding: none;
  padding-left: 3%;


}

.row-action{
  color:#003399;
  font-size:90%;

}



.PositionA{
  color:#33cc33;
  font-size:100%;

}

.PositionB{
  color:#66ccff;
  font-size:100%;
}
    
    
.PositionC{
  color:#0033cc;
  font-size:100%;
}
    
.PositionD{
  color:#ff9900;
  font-size:100%;
}
    
.PositionE{
  color:#ff5050;
  font-size:100%;
}
    
.PositionF{
  color:#cc3300;
  font-size:100%;
}
    

.trendcontainer {
  position: absolute;
  top: 14%;
  left: 36%;
  width: 10%; 
  height:78%;

}


.trendtext {
  color: #1B329E;
  font-size:60%;
  border: none;
  text-align: center; 
  padding: 0.8%; 
}




</style>


</head>
<body>

<div class="dashboardcontainer">

<img src="fink.png"> 




	<div class="accounttablecontainer">

	<table class="table">
	<tbody>
	<tr class="heading">
		<th>Pair</th>
		<th>Holding</th>
	</tr>

<?php

$fink=mysqli_connect("206.189.209.201","fink","Amm02o16!","Fink");


// Check connection
if (mysqli_connect_errno())
{
echo "Failed to connect to MySQL: " . mysqli_connect_error();
}

$result = mysqli_query($fink,"SELECT `Pair`, `Position`, StopLoss, `ReturnLimit`,`HoldBTC` FROM `Pairs` WHERE HoldBTC > 0.0005 ORDER BY HoldBTC DESC");


while($row = mysqli_fetch_array($result))
{
    
$r = $row['Position'] / $row['ReturnLimit'];
$s = ($row['Position'] - $row['StopLoss']) * 100;

if ($row['Position'] >= 1 && $r >= 0.9)
{
  $rowClass = "PositionA";
}
elseif ($row['Position'] >= 1 && $r < 0.8 && $r >= 0.8)
{
  $rowClass = "PositionB";
}
elseif ($row['Position'] >= 1 && $r < 0.4)
{
  $rowClass = "PositionC";
}
elseif ($row['Position'] < 1 && $s > 10)
{
  $rowClass = "PositionD";
}
elseif ($row['Position'] < 1 &&  $s <= 10 && $s >= 5)
{
  $rowClass = "PositionE";
}
elseif ($row['Position'] < 1 && $s < 5)
{
  $rowClass = "PositionF";
}
    
    

echo "<tr class='".$rowClass."'>";

echo "<td  class='actionrow'>" . $row['Pair'] . "</td>";
echo "<td  class='actionrow'>" . $row['HoldBTC'] . "</td>";
echo "</tr>";
}


echo "</tbody>";
echo "</table>";




$result = mysqli_query($fink,"SELECT `BTC`, `USD` FROM `AccountBalance` ORDER BY DateTime DESC LIMIT 1");
$Accountrow = mysqli_fetch_array($result)



?>

</div>

<div class="btcamount">
		<p class="BTC"> Total BTC: <?php echo $Accountrow[0] . " BTC / $" . $Accountrow[1] ?> </p> 
	</div>



<div class="actionstablecontainer">

	<table class="table">
	<tbody>
	<tr class="heading">
		<th>Pair</th>
		<th>Action</th>
		<th>Amount</th>
		<th>Price</th>
		<th>Time</th>
	</tr>




<?php


// Check connection
if (mysqli_connect_errno())
{
echo "Failed to connect to MySQL: " . mysqli_connect_error();
}

$result = mysqli_query($fink,"select * from AccountHistory order by ActionTime desc limit 6");



while($row = mysqli_fetch_array($result))
{

$ReturnBTC = $row['Amount'] * $row['Price'];


echo "<tr class= row-action '>";

echo "<td class='actionrow'>" . $row['Pair'] . "</td>";
echo "<td class='actionrow'>" . $row['Action'] . "</td>";
echo "<td class='actionrow'>" . $ReturnBTC . "</td>";
echo "<td class='actionrow'>" . $row['Price'] . "</td>";
echo "<td class='actionrow'>" . $row['ActionTime'] . "</td>";
echo "</tr>";
}


echo "</tbody>";
echo "</table>";


?>


</div> 	



	
</div>


<div class="SignalHistoryContainer">

	<table class="table">
	<tbody>
	<tr class="heading">
		<th>Pair</th>
	</tr>




<?php


// Check connection
if (mysqli_connect_errno())
{
echo "Failed to connect to MySQL: " . mysqli_connect_error();
}

$result = mysqli_query($fink,"SELECT `Pair`, `Entry` FROM `Pairs` WHERE TradeSignal = 1 ORDER BY Entry asc limit 10");



while($row = mysqli_fetch_array($result))
{
    
if ($row['Entry'] < 0.9 && $row['Entry'] >= 0.8)
{
  $rowClass = "PositionA";
}
elseif ($row['Entry'] < 1 && $row['Entry'] >= 0.9)
{
  $rowClass = "PositionB";
}
elseif ($row['Entry'] < 1.01 && $row['Entry'] >= 1)
{
  $rowClass = "PositionC";
}
elseif ($row['Entry'] < 1.05 && $row['Entry'] >= 1.01)
{
  $rowClass = "PositionD";
}
elseif ($row['Entry'] < 1.1 && $row['Entry'] >= 1.05)
{
  $rowClass = "PositionE";
}
elseif ($row['Entry'] >= 1.1)
{
  $rowClass = "PositionF";
}
    

echo "<tr class='".$rowClass."'>";


echo "<td class='actionrow'>" . $row['Pair'] . "</td>";
echo "</tr>";
}


echo "</tbody>";
echo "</table>";


mysqli_close($fink);
?>


</div> 	



</body>
</html>

