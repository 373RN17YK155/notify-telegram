create table subscribtion(
  id TEXT PRIMARY KEY,
  chatId TEXT,
  cookie TEXT,
);


create table relatedTravel(
  id INTEGER PRIMARY KEY,
  subscribtionId TEXT,
  FOREIGN KEY(subscribtionId) REFERENCES subscribtion(id)
); 
