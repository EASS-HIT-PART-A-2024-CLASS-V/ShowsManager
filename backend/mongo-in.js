//this file is to insert an admin user

db = db.getSiblingDB('test');

db.createUser({
  user: "admin",
  pwd: "admin",
  roles: [
    {
      role: "readWrite",
      db: "test"
    }
  ]
});