set -e

echo $MONGO_INITDB_DATABASE
echo $MONGO_INITDB_USERNAME
echo $MONGO_INITDB_PASSWORD

mongosh <<EOF
use $MONGO_INITDB_DATABASE

db.createUser({
  user: '$MONGO_INITDB_USERNAME',
  pwd: '$MONGO_INITDB_PASSWORD',
  roles: [{
    role: 'readWrite',
    db: '$MONGO_INITDB_DATABASE'
  }]
})
EOF