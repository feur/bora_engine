-- phpMyAdmin SQL Dump
-- version 4.5.4.1deb2ubuntu2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jul 04, 2018 at 04:48 PM
-- Server version: 5.7.22-0ubuntu0.16.04.1
-- PHP Version: 7.0.30-0ubuntu0.16.04.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `Fink`
--

-- --------------------------------------------------------

--
-- Table structure for table `AccountBalance`
--

CREATE TABLE `AccountBalance` (
  `PID` int(11) DEFAULT NULL,
  `BTC` float DEFAULT NULL,
  `USD` float NOT NULL,
  `DateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `AccountHistory`
--

CREATE TABLE `AccountHistory` (
  `PID` int(11) DEFAULT NULL,
  `Pair` varchar(20) DEFAULT NULL,
  `Amount` float DEFAULT NULL,
  `Price` float DEFAULT NULL,
  `Action` varchar(4) NOT NULL,
  `ActionTime` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Components`
--

CREATE TABLE `Components` (
  `Unit` varchar(20) NOT NULL,
  `PID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `Components`
--

INSERT INTO `Components` (`Unit`, `PID`) VALUES
('account', 22359);

-- --------------------------------------------------------

--
-- Table structure for table `ExLog`
--

CREATE TABLE `ExLog` (
  `Pair` varchar(20) DEFAULT NULL,
  `Action` varchar(10) DEFAULT NULL,
  `Price` float DEFAULT NULL,
  `Profit` float DEFAULT NULL,
  `Time` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `Pairs`
--

CREATE TABLE `Pairs` (
  `Pair` varchar(10) DEFAULT NULL,
  `Currency` varchar(20) DEFAULT NULL,
  `TradeSignal` int(11) DEFAULT NULL,
  `PID` int(11) DEFAULT NULL,
  `HoldBTC` float DEFAULT NULL,
  `UpdateTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `Pairs`
--

INSERT INTO `Pairs` (`Pair`, `Currency`, `TradeSignal`, `PID`, `HoldBTC`, `UpdateTime`) VALUES
('BTC-IOC', 'IOC', 0, 22362, 0.000570493, '2018-07-02 08:34:00'),
('BTC-SPR', 'SPR', 0, 22365, 0, '2018-07-02 08:34:00'),
('BTC-SIB', 'SIB', 1, 22369, 0.0403509, '2018-07-02 08:36:05'),
('BTC-OK', 'OK', 0, 22372, 0.000011997, '2018-07-02 08:36:05'),
('BTC-ADT', 'ADT', 0, 22379, 0.000041554, '2018-07-02 08:36:05'),
('BTC-TRUST', 'TRUST', 0, 22383, 0.00187485, '2018-07-02 08:36:05'),
('BTC-ZCL', 'ZCL', 0, 22384, 0, '2018-07-02 08:36:05'),
('BTC-GAME', 'GAME', 0, 22387, 0.000039616, '2018-07-02 08:36:05'),
('BTC-ENRG', 'ENRG', 0, 22390, 0, '2018-07-02 08:36:05'),
('BTC-PART', 'PART', 0, 22393, 0, '2018-07-02 08:36:05'),
('BTC-EXP', 'EXP', 1, 22396, 0, '2018-07-02 08:36:05'),
('BTC-COVAL', 'COVAL', 0, 22400, 0, '2018-07-02 08:36:05'),
('BTC-KORE', 'KORE', 0, 22404, 0.00095476, '2018-07-02 08:36:05'),
('BTC-FCT', 'FCT', 0, 22408, 0.000009135, '2018-07-02 08:36:05'),
('BTC-MEME', 'MEME', 0, 22414, 0, '2018-07-02 08:36:05'),
('BTC-PIVX', 'PIVX', 0, 22420, 0.0645403, '2018-07-02 08:36:05'),
('BTC-SPHR', 'SPHR', 0, 22423, 0.000035621, '2018-07-02 08:36:05'),
('BTC-EXCL', 'EXCL', 1, 22428, 0.000039305, '2018-07-02 08:36:05'),
('BTC-XZC', 'XZC', 0, 22433, 0, '2018-07-02 08:36:05'),
('BTC-ION', 'ION', 0, 22437, 0.000011232, '2018-07-02 08:36:05'),
('BTC-XCP', 'XCP', 0, 22440, 0.0355307, '2018-07-02 08:36:05'),
('BTC-GNO', 'GNO', 0, 22444, 0, '2018-07-03 04:16:37'),
('BTC-LBC', 'LBC', 0, 22448, 0, '2018-07-03 04:16:37'),
('BTC-BCY', 'BCY', 0, 22454, 0, '2018-07-03 04:16:37'),
('BTC-ARDR', 'ARDR', 0, 22456, 0, '2018-07-03 04:16:37'),
('BTC-MER', 'MER', 0, 22460, 0.000013071, '2018-07-03 04:16:37'),
('BTC-NXT', 'NXT', 0, 22463, 0, '2018-07-03 04:16:37'),
('BTC-DOPE', 'DOPE', 0, 22469, 0.00805227, '2018-07-03 04:16:37');

-- --------------------------------------------------------

--
-- Table structure for table `SignalLog`
--

CREATE TABLE `SignalLog` (
  `Pair` varchar(20) DEFAULT NULL,
  `BuyPrice` float DEFAULT NULL,
  `SellPrice` float DEFAULT NULL,
  `TimeInterval` varchar(20) DEFAULT NULL,
  `Time` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
