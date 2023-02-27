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