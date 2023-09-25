# first setups
    1. in sticker/grasser/react, 
        - check your node, npm version is 18 lts / latest.
        - npm install
        - npm run build
    2. in ./ ,
        - check your python version is 3 and latest.
        - python -m venv pyvenv
        - autovenv.bat or pyvenv\Scripts\activate
        - upgrade the pip.
        - pip install -r requirements.txt
    3. in ./ , 
        - there are no migrations in this project. so,
        - manage.py createsuperuser
        - manage.py makemigrations
        - manage.py migrate
    4. in ./ ,
        - manage.py runserver
    5. (for docker building) in ./ ,
        - docker build -t ...
 

# when you want to test sth in local
    1. after adjusting codes, 
        - check if docker desktop is running.
        - execute autogit.bat
        - run "commit docker". it will automatically generate the 'ghcr.io/enzoescipy/sticker_grasser:pending' tagged image in docker.
        - open bash, and run "docker run -d -p 8000:8000 ghcr.io/enzoescipy/sticker_grasser:pending".
        - test sth you want.
    2. if you wan to close the server,
        - check if docker desktop is running.
        - run "docker ps -a"
        - kill the running container like "docker kill <container_hash>"
        - remove the dead container like "docker rm <container_hash>"

# when you want to commit sth to git repo
    - execute autogit.bat
    - run "commit git". 
    - for this way, .bat will automatically do the,
        1. commit every sub-modules.
        2. commit the main repo.

# when you want to push the everything in this repo
    - autogit.bat "push git" will be work just great.
    - autogit.bat "push docker" will do,
        - push current 'ghcr.io/enzoescipy/sticker_grasser:pending' image into the github container regisistry, or, the github packages.
        - image's name will be decided to 'ghcr.io/enzoescipy/sticker_grasser:<git_commit_hash>' which <git_commit_hash> is newist git repo's commit's hashtag.
        - So, you can now download that image in the server by run the "docker pull ghcr.io/enzoescipy/sticker_grasser:<git_commit_hash>".
        - WARNING : do not download :latest tag. it can be not the latest.
    - And the autogit.bat "push git docker" will first do git commit -> git push -> and then docker push.

# when you want to re-build the cloud server for this project
    - make instance by non-arm process, and centos 7.
    - clean install the docker
        - yum update
        - yum install yum-utils
        - yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        - yum install docker-ce docker-ce-cli containerd.io
    - start docker daemon
        - systemctl start docker (you have to run this command everytime you reboot your instance)
