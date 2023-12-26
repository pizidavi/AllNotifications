
CREATE TABLE `users` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `telegram_id` varchar(20) NOT NULL,
  PRIMARY KEY (`user_id`,`telegram_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `comics` (
  `element_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `title` varchar(200) NOT NULL,
  `number` varchar(50) DEFAULT NULL,
  `lang` varchar(5) NOT NULL DEFAULT 'it',
  `provider` varchar(5) DEFAULT NULL,
  `last_update` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `disabled` bool NOT NULL DEFAULT 0,
  PRIMARY KEY (`element_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`),
  UNIQUE (`user_id`,`title`,`lang`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `comics_ignored` (
  `element_id` int(11) NOT NULL AUTO_INCREMENT,
  `provider` varchar(5) DEFAULT NULL,
  `createdAt` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`element_id`, `provider`),
  FOREIGN KEY (`element_id`) REFERENCES `comics`(`element_id`),
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
