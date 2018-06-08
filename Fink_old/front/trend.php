<html>
<head>

<style type="text/css">

body {
  background-color: #000000;
}

table {
    border-collapse: collapse;
    border:1px solid #C0A002;
    width: 98%; 
    
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
  color: #FF5615;
  font-size:10pt;
  border: none;
  text-align: center; 
  padding: 0.8%; 
}


</style>


</head>
<body>

<table>
<tbody>
<tr class="heading">
<th>Pair</th>
</tr>

    

<?php
//$fink=mysqli_connect("138.197.194.3","dev","5AKC08noMTwx9lG2","Fink");
//$fink=mysqli_connect("localhost","root","Amm02o16!","Fink");
$edel=mysqli_connect("138.197.194.3","user","QkK9GTOQuia5DjzC","Edel");

// Check connection
if (mysqli_connect_errno())
{
echo "Failed to connect to MySQL: " . mysqli_connect_error();
}


$result = mysqli_query($edel,"SELECT Pair,Watch FROM Pair_List WHERE Watch=1;");


while($row = mysqli_fetch_array($result))
{
echo "<tr>";
echo "<td>" . $row['Pair'] . "</td>";

echo "</tr>";
}
echo "</tbody>";
echo "</table>";

mysqli_close($edel);
?>



	
	
</body>
</html>
