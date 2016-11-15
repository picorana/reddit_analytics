from pattern.web    import Twitter, plaintext
from pattern.en     import tag
from pattern.vector import KNN, count

twitter = Twitter(language='en')


for tweet in twitter.search('"more important than"'):
   print plaintext(tweet.text)