docker image tag ghcr.io/enzoescipy/sticker_grasser:pending %1
docker rmi ghcr.io/enzoescipy/sticker_grasser:pending
docker push %1
