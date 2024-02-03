create table subscribtion(
  id INTEGER PRIMARY KEY,
  cookie TEXT,
  isRuning BOOLEAN
);


create table relatedTravel(
  id INTEGER PRIMARY KEY,
  subscribtionId INTEGER,
  FOREIGN KEY(subscribtionId) REFERENCES subscribtion(id)
); 
