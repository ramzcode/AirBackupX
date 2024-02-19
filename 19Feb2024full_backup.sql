-- MySQL dump 10.13  Distrib 5.7.42, for osx10.15 (x86_64)
--
-- Host: 127.0.0.1    Database: passwords_db
-- ------------------------------------------------------
-- Server version	5.7.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `passwords_db`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `passwords_db` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `passwords_db`;

--
-- Table structure for table `backup_records`
--

DROP TABLE IF EXISTS `backup_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `backup_records` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `backup_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `device_name` varchar(255) NOT NULL,
  `site_name` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  `exit_status` varchar(255) DEFAULT NULL,
  `file_name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=88 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `backup_records`
--

LOCK TABLES `backup_records` WRITE;
/*!40000 ALTER TABLE `backup_records` DISABLE KEYS */;
INSERT INTO `backup_records` VALUES (1,'2023-10-02 06:31:04','CiscoRouter1','SiteA','Router','admin','succeeded','backup_file_20231002.txt'),(2,'2023-10-02 07:05:52','CiscoRouter2','SiteBB','Router','admin','failed','backup_file_20231002.txt'),(3,'2023-10-04 18:09:05','192.168.1.105','GNS3-Local','IOS','admin','failed','NA'),(4,'2023-10-04 18:19:16','192.168.1.105','GNS3-Local','IOS','admin','failed','NA'),(5,'2023-10-04 18:21:07','192.168.1.105','GNS3-Local','IOS','admin','failed','NA'),(6,'2023-10-04 18:23:48','192.168.1.105','GNS3-Local','IOS','admin','failed','NA'),(7,'2023-10-04 18:30:02','192.168.1.105','GNS3-Local','IOS','admin','failed','NA'),(8,'2023-10-04 18:36:46','192.168.1.105','GNS3-Local','IOS','admin','success','/Users/ram/Downloads/AirBackupX/Backups/config_backup_192.168.1.105_2023-10-04_18-36-45.txt'),(9,'2023-10-04 18:51:50','192.168.1.105','GNS3-Local','IOS','admin','Success','/Users/ram/Downloads/AirBackupX/Backups/config_backup_192.168.1.105_2023-10-04_18-51-50.txt'),(10,'2023-10-04 18:52:08','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(11,'2023-10-04 19:00:05','192.168.1.105','GNS3-Local','IOS','admin','Success','/Users/ram/Downloads/AirBackupX/Backups/config_backup_192.168.1.105_2023-10-04_19-00-04.txt'),(12,'2023-10-04 19:00:19','192.168.1.112','GNS3-Local','IOS','admin','Success','/Users/ram/Downloads/AirBackupX/Backups/config_backup_192.168.1.112_2023-10-04_19-00-19.txt'),(13,'2023-10-04 19:04:22','192.168.1.105','GNS3-Local','IOS','admin','Success','/Users/ram/Downloads/AirBackupX/Backups/config_backup_192.168.1.105_2023-10-04_19-04-22.txt'),(14,'2023-10-04 19:04:36','192.168.1.112','GNS3-Local','IOS','admin','Success','/Users/ram/Downloads/AirBackupX/Backups/config_backup_192.168.1.112_2023-10-04_19-04-35.txt'),(15,'2023-10-04 19:09:59','192.168.1.105','GNS3-Local','IOS','admin','Success','/Users/ram/Downloads/AirBackupX/Backups/config_backup_192.168.1.105_2023-10-04_19-09-59.txt'),(16,'2023-10-04 19:10:34','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(17,'2023-10-04 19:26:21','192.168.1.105','GNS3-Local','IOS','admin','Success','/Users/ram/Downloads/AirBackupX/Backups/config_backup_192.168.1.105_2023-10-04_19-26-20.txt'),(18,'2023-10-04 19:27:21','192.168.1.105','GNS3-Local','IOS','admin','Success','/Users/ram/Downloads/AirBackupX/Backups/config_backup_192.168.1.105_2023-10-04_19-27-20.txt'),(19,'2023-10-04 19:27:39','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(20,'2023-10-04 19:29:33','192.168.1.105','GNS3-Local','IOS','admin','Success','/Users/ram/Downloads/AirBackupX/Backups/config_backup_192.168.1.105_2023-10-04_19-29-33.txt'),(21,'2023-10-04 19:29:51','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(22,'2023-10-04 19:31:31','192.168.1.105','GNS3-Local','IOS','admin','Success','/Users/ram/Downloads/AirBackupX/Backups/config_backup_192.168.1.105_2023-10-04_19-31-31.txt'),(23,'2023-10-04 19:31:49','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(24,'2023-10-04 19:41:06','192.168.1.105','GNS3-Local','IOS','admin','Success','/Users/ram/Downloads/AirBackupX/Backups/config_backup_192.168.1.105_2023-10-04_19-41-05.txt'),(25,'2023-10-04 19:41:24','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(26,'2023-10-04 20:01:27','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(27,'2023-10-04 20:01:45','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(28,'2023-10-04 20:10:37','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(29,'2023-10-04 20:10:55','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(30,'2023-10-04 20:20:08','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(31,'2023-10-04 20:20:26','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(32,'2023-10-04 20:36:32','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(33,'2023-10-04 20:36:50','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(34,'2023-10-04 20:55:52','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(35,'2023-10-04 20:56:10','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(36,'2023-10-04 21:08:53','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(37,'2023-10-04 21:09:11','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(38,'2023-10-04 21:14:11','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(39,'2023-10-04 21:14:29','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(40,'2023-10-04 21:16:47','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(41,'2023-10-04 21:17:05','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(42,'2023-10-04 21:21:01','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(43,'2023-10-04 21:22:35','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(44,'2023-10-04 21:24:53','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(45,'2023-10-04 21:25:52','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(46,'2023-10-04 21:26:10','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(47,'2023-10-04 21:27:33','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(48,'2023-10-04 21:27:51','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(49,'2023-10-04 21:32:09','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(50,'2023-10-04 21:32:27','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(51,'2023-10-04 21:33:32','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(52,'2023-10-04 21:33:50','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(53,'2023-10-04 21:35:55','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(54,'2023-10-04 21:36:13','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(55,'2023-10-04 21:51:04','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(56,'2023-10-04 21:51:22','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(57,'2023-10-04 21:52:29','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(58,'2023-10-04 21:52:47','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(59,'2023-10-04 23:18:34','CiscoRouter2','SiteBB','Router','admin','Failed','backup_file_20231002.txt'),(60,'2023-10-04 23:46:48','CiscoRouter2','SiteBB','Router','admin','Failed','backup_file_20231002.txt'),(61,'2023-10-05 00:09:46','CiscoRouter2','SiteBB','Router','admin','Failed','backup_file_20231002.txt'),(62,'2023-10-05 00:31:40','CiscoRouter2','SiteBB','Router','admin','Failed','backup_file_20231002.txt'),(63,'2023-10-05 00:34:51','CiscoRouter2','SiteBB','Router','admin','Failed','backup_file_20231002.txt'),(64,'2023-10-05 00:35:17','CiscoRouter2','SiteBB','Router','admin','Failed','backup_file_20231002.txt'),(65,'2023-10-05 00:36:46','CiscoRouter2','SiteBB','Router','admin','Failed','backup_file_20231002.txt'),(66,'2023-10-05 00:38:43','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(67,'2023-10-05 00:39:01','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(68,'2023-10-05 01:12:16','CiscoRouter2','SiteBB','Router','admin','Failed','backup_file_20231002.txt'),(69,'2023-10-05 01:12:39','CiscoRouter2','SiteBB','Router','admin','Failed','backup_file_20231002.txt'),(70,'2023-10-05 01:39:52','CiscoRouter2','SiteBB','Router','admin','Failed','backup_file_20231002.txt'),(71,'2023-10-05 02:42:49','CiscoRouter2','SiteBB','Router','admin','Failed','backup_file_20231002.txt'),(72,'2023-10-05 02:53:15','CiscoRouter2','SiteBB','Router','admin','Failed','backup_file_20231002.txt'),(73,'2023-10-05 02:59:29','CiscoRouter6','SiteBB','Router','admin','Failed','backup_file_20231002.txt'),(74,'2023-10-05 03:06:13','CiscoRouter6','SiteBB','Router','admin','Failed','backup_file_20231002.txt'),(75,'2023-10-05 03:06:29','CiscoRouter6','SiteBB','Router','admin','Failed','backup_file_20231002.txt'),(76,'2023-10-05 03:06:38','CiscoRouter6','SiteBB','Router','admin','Failed','backup_file_20231002.txt'),(77,'2023-10-05 03:14:05','om','SiteBB','Router','admin','Failed','backup_file_20231002.txt'),(78,'2023-10-05 03:14:52','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(79,'2023-10-05 03:15:10','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(80,'2023-10-05 19:38:08','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(81,'2023-10-05 19:38:26','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(82,'2023-10-06 12:29:54','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(83,'2023-10-06 12:30:12','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(84,'2023-10-06 12:35:24','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(85,'2023-10-06 12:35:42','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA'),(86,'2023-10-12 19:46:55','192.168.1.105','GNS3-Local','IOS','admin','Failed','NA'),(87,'2023-10-12 19:47:13','192.168.1.112','GNS3-Local','IOS','admin','Failed','NA');
/*!40000 ALTER TABLE `backup_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cron_jobs`
--

DROP TABLE IF EXISTS `cron_jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cron_jobs` (
  `job_id` varchar(255) NOT NULL,
  `site_name` varchar(255) DEFAULT NULL,
  `script_path` varchar(255) DEFAULT NULL,
  `minute` varchar(10) DEFAULT NULL,
  `hour` varchar(10) DEFAULT NULL,
  `day` varchar(10) DEFAULT NULL,
  `month` varchar(10) DEFAULT NULL,
  `day_of_week` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`job_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cron_jobs`
--

LOCK TABLES `cron_jobs` WRITE;
/*!40000 ALTER TABLE `cron_jobs` DISABLE KEYS */;
INSERT INTO `cron_jobs` VALUES ('af843fb7-5c3f-41cd-86c8-36f9adc8eb95','GNS3-Local','/Users/ram/Downloads/AirBackupX/scripts/GNS3-Local.py','2','2','2','2','2'),('b0008407-d04e-4b32-8d6e-93a5e48cd841','GNS3-Local','/Users/ram/Downloads/AirBackupX/scripts/GNS3-Local.py','6','6','6','6','6');
/*!40000 ALTER TABLE `cron_jobs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `groups`
--

DROP TABLE IF EXISTS `groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups`
--

LOCK TABLES `groups` WRITE;
/*!40000 ALTER TABLE `groups` DISABLE KEYS */;
INSERT INTO `groups` VALUES (32,'GNS3-Local'),(12,'helo'),(33,'love'),(31,'MANA');
/*!40000 ALTER TABLE `groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `passwords`
--

DROP TABLE IF EXISTS `passwords`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `passwords` (
  `username` varchar(255) DEFAULT NULL,
  `device` varchar(255) DEFAULT NULL,
  `encrypted_password` blob,
  `group_name` varchar(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  UNIQUE KEY `device` (`device`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `passwords`
--

LOCK TABLES `passwords` WRITE;
/*!40000 ALTER TABLE `passwords` DISABLE KEYS */;
INSERT INTO `passwords` VALUES ('admin','192.168.1.105',_binary 'gAAAAABlHGozj5QUdzQ84b7WwUbH6Z7ovV1WkraRBrTAsOX3h9zkH2Q0Gca-UAx8nfDxpE-EUVX9uves2A5Y6EKUFFMdUdG6iA==','GNS3-Local','IOS'),('admin','192.168.1.112',_binary 'gAAAAABlHR3vzMcJhir2rTSpxvjtgvQ3quip77bwqS8QV4_DcgLco5dPk_woj3kScI4_tUuDTeeZO2BjVgNjyNTynqWmi6viWA==','GNS3-Local','IOS');
/*!40000 ALTER TABLE `passwords` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `smtp_config`
--

DROP TABLE IF EXISTS `smtp_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `smtp_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `smtp_server` varchar(255) DEFAULT NULL,
  `smtp_port` int(11) DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  `encrypted_password` blob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `smtp_config`
--

LOCK TABLES `smtp_config` WRITE;
/*!40000 ALTER TABLE `smtp_config` DISABLE KEYS */;
INSERT INTO `smtp_config` VALUES (1,'smtp.gmail.com',587,'ramzcodealert@gmail.com',_binary 'gAAAAABlu68XdrDfK2R61JPAlAobnfyXNb9ESkK9knuuCgSqw-K7KjFXpRCuyFfh7NnNCort-vnsLYILa6ajRhWhYm-Lan_-8hV-sRfkRUC6p4nY5pjFcCk=');
/*!40000 ALTER TABLE `smtp_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `types`
--

DROP TABLE IF EXISTS `types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `types`
--

LOCK TABLES `types` WRITE;
/*!40000 ALTER TABLE `types` DISABLE KEYS */;
INSERT INTO `types` VALUES (10,'ASA'),(11,'IOS'),(17,'SHIVA');
/*!40000 ALTER TABLE `types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `emailID` varchar(255) NOT NULL,
  `role` varchar(255) NOT NULL,
  `totp_secret` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (5,'2222','pbkdf2:sha256:600000$bWDqmAndZApK6VGI$d5cd74dc9685a4ef4ec7fa6ea0dbbb434ad8fcc9d080c26020ec19e631757808','ponnurangam.h@gmail.com','admin',NULL),(28,'superman','pbkdf2:sha256:600000$uXYPN63Xc6KfkS2I$493b7b357f6792331ef2fa3362434858cd653835339cd04324b1c1bb15d9adb7','ponnurangam.h@gmail.com','admin','ZUUA5IGE4SYBFLVYFABD4BV7KPT2H4W5');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-02-19 20:03:01
