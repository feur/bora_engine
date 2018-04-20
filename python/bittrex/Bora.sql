-- phpMyAdmin SQL Dump
-- version 4.5.4.1deb2ubuntu2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Apr 20, 2018 at 02:21 PM
-- Server version: 5.7.21-0ubuntu0.16.04.1
-- PHP Version: 7.0.28-0ubuntu0.16.04.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `Bora`
--

-- --------------------------------------------------------

--
-- Table structure for table `Pairs`
--

CREATE TABLE `Pairs` (
  `Pair` varchar(10) DEFAULT NULL,
  `Rating` float DEFAULT NULL,
  `TradeSignal` int(11) DEFAULT NULL,
  `PID` int(11) DEFAULT NULL,
  `Bought` float DEFAULT NULL,
  `Hold` tinyint(1) DEFAULT NULL,
  `UpdateTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `Pairs`
--

INSERT INTO `Pairs` (`Pair`, `Rating`, `TradeSignal`, `PID`, `Bought`, `Hold`, `UpdateTime`) VALUES
('BTC-XLM', 3709, 2, 11891, NULL, NULL, '2018-04-19 06:03:03'),
('BTC-ADA', 3423, 2, 11895, NULL, NULL, '2018-04-19 06:05:00'),
('BTC-LTC', 2318, 2, 11899, NULL, NULL, '2018-04-19 06:05:09'),
('BTC-OMG', 2738, 2, 11883, NULL, NULL, '2018-04-19 06:05:28'),
('BTC-ARK', 2578, 2, 11887, NULL, NULL, '2018-04-19 06:05:39'),
('BTC-BCC', 3158, 2, 11866, NULL, NULL, '2018-04-19 06:05:59'),
('BTC-NEO', 3166, 2, 11879, NULL, NULL, '2018-04-19 06:06:14'),
('BTC-STEEM', 1189, 3, 11862, NULL, NULL, '2018-04-19 06:06:54'),
('BTC-TRX', 2520, 3, 11903, NULL, NULL, '2018-04-19 06:07:09'),
('BTC-SALT', 3123, 2, 11907, NULL, NULL, '2018-04-19 06:07:29');

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
