<html>
<head>

<style type="text/css">

body, html {
  background-color: #000000;
  margin:0;
  padding:0;
}

table {
    border-collapse: collapse;
    border:1px solid #C0A002;
    width: 100%; 
    height:100%;
    
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
  color: #FFFFFF;
  font-size:10pt;
  border: none;
  text-align: center; 
  padding: 0.8%; 
}

.BTC {

  color: #FFFFFF;
  font-size:16pt;
  font-weight: bold;

}

img {

  width: 95%;
  height: 97%;
  padding-left: 1%; 
  padding-top: 1%; 

}

.container {
  position: relative;
}


.tablecontainer {
  position: absolute;
  top: 13%;
  left: 6%;
  width: 90%; 
  height:71%;

}


.btcamount {
  position: absolute;
  top: 88%;
  left: 8%;

}



</style>


</head>
<body>

<div class="container">
<img src="account.png"> 


<div class="tablecontainer">

<table>
<tbody>
<tr class="heading">
	<th>Pair</th>
	<th>Amount</th>
	<th>In BTC</th>
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

$result = mysqli_query($fink,"SELECT * FROM Pairs WHERE HoldBTC > 0 ORDER BY HoldBTC DESC ");


while($row = mysqli_fetch_array($result))
{
echo "<tr>";
echo "<td>" . $row['Pair'] . "</td>";
echo "<td>" . $row['Hold'] . "</td>";
echo "<td>" . $row['HoldBTC'] . "</td>";
echo "</tr>";
}


$result = mysqli_query($fink,"SELECT * FROM AccountBalance ORDER BY DateTime DESC LIMIT 1");
$row = mysqli_fetch_row($result);


echo "</tbody>";
echo "</table>";



mysqli_close($fink);
?>





</div>

<div class="btcamount">
<p class="BTC"> Total BTC Detected: <?php echo $row[1] . " / $" . $row[2] ?> </p> 
<div>

</div>


	
	
</body>
</html>
