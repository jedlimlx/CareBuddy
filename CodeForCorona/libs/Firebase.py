import pyrebase

config = {
  "apiKey": "AIzaSyDFk0oWfOQNO2hsKnKL2XRDR-74lNJEhoo",
  "authDomain": "codeforcorona-8ca30.firebaseapp.com",
  "databaseURL": "https://codeforcorona-8ca30.firebaseio.com",
  "storageBucket": "codeforcorona-8ca30.appspot.com"
}

firebase = pyrebase.initialize_app(config)

auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()
