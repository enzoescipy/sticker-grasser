docker image tag ghcr.io/scika/sticker_grasser:pending %1
docker rmi ghcr.io/scika/sticker_grasser:pending
docker push %1
