# README

## Install

```{bash}
pip install \
       Django==4.1.3 \
       djangorestframework==3.14.0 \
       channels==4.0.0 \
       channels-redis==4.0.0 \
       daphne==4.0.0 \
       pytest-asyncio==0.20.1 \
       pytest-django==4.5.2 \
       Pillow==9.3.0 \
       djangorestframework-simplejwt==5.2.2 \
       psycopg2-binary==2.9.5
pip install numpy
pip install pandas
```

## Server
```{bash}
django-admin startproject soccerstars .
poetry run python manage.py startapp game
python manage.py startapp authentication
```

## Client
```{bash}
# Ensure you're back at the root directory
cd ..

# Create a new React app in the 'client' directory
npx create-react-app client

# Navigate into your newly created React app
cd client

# Add Axios for making HTTP requests, and other libraries you might need
npm install axios rxjs

# Start the React development server
npm start
```


## Sources

- Taxi app: [real-time-app-with-django-channels-and-angular](https://testdriven.io/courses/real-time-app-with-django-channels-and-angular/part-one-getting-started/)