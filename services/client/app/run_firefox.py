from marionette_driver.marionette import Marionette

# Initialiser la connexion Marionette
client = Marionette('localhost', port=2828)
client.start_session()

# Ouvrir une URL
client.navigate('https://www.example.com')

# Obtenir le titre de la page
title = client.title
print(f'Title: {title}')

# Fermer la session
client.delete_session()
