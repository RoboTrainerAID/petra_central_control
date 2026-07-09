docker run \
    -d \
    --name mongodb \
    --env-file .env \
    -v $PWD/mongodb/initdb.d/:/docker-entrypoint-initdb.d/ \
    -p 27017:27017 \
    --rm \
    mongo && \
    
echo "MongoDB started"
    # -v $PWD/mongodb/data:/data/db/ \