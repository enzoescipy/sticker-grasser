docker image tag ghcr.io/scika/sticker_grasser_temp:pending %1
docker rmi ghcr.io/scika/sticker_grasser_temp:pending
docker push %1
