# FilterCloud

[https://filter.poe.gg](https://filter.poe.gg)

## How To Run
 * Install [Docker 17.05](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/)
 * Install docker-compose 1.16, e.g. via `pip install docker-compose`
 * `docker-compose build`
 * `docker-compose up -d`
 * You should now be able to access it at localhost:8080/filter/index.html

When running for the first time, you also need to manually create some indexes on
the database. I will automate that in the future, but for now do this:
 * `docker exec -ti filtercloud-db mongo`
 * `use filterforge`
 * `db.users.createIndex({"id":1},{unique:true});`
 * `db.users.createIndex({"name":1},{unique:true});`
 * `db.styles.createIndex({"owner":1, "name": 1},{unique:true});`
 * `db.configs.createIndex({"owner":1, "name": 1},{unique:true});`
