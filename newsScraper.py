from gnews import GNews # needed for google news api
from newspaper import Article # needed for article scraping
from googlenewsdecoder import gnewsdecoder # needed for decoding google news api

import yaml # needed for reading yaml config file
import json # needed for reading json objects from the llm
import os # needed for folder creation

from geopy.geocoders import Nominatim # needed for geolocation

from ollama import chat # needed for LLM
from ollama import ChatResponse # needed for LLM

import time # needed for timestamping

# Only needed for testing
import random # needed for random number generation

# load config settings
with open("./configs/context.yaml", "r") as ymlfile:
    context = yaml.safe_load(ymlfile)

# Configure the LLM settings
model_id = context["llm"]["ID"]
modelContext = context["llm"]["CONTEXT"]
modelJSON = [] # list to hold the JSON output of the LLM

# Create the incidents folder if it doesn't exist
if not os.path.exists("./incidents"):
    os.makedirs("./incidents")


# Configure the geolocation object
geolocator = Nominatim(user_agent="newsAnalyzer")

# Configure the Google News object
googleNews = GNews(language=context["news"]["LANGUAGE"], country=context["news"]["COUNTRY"], period=context["news"]["LOOKBACK"])



def getHistory():
    """
    Function to get the history of all existing  and return it as a context string
    """
    incidents = []
    for file in os.listdir("./incidents"):
        with open(f"./incidents/{file}", "r") as incident:
            incidents.append(json.load(incident))

    historyContext = "This is the list of summarized incidents that have been detected so far.  If a news story is similar to any of these incidents, it is not unique: \n"

    for incident in incidents:
        historyContext += f"Title: {incident['title']}, Date: {incident['date']}, Summery: {incident['summery']} \n"

    return historyContext










# TODO: Put this in a main function

# get the history context of all current incidents
historyContext = getHistory() 

# gets all drone stories from the past hour as a json list
newsJSON = googleNews.get_news(context["news"]["TOPIC"])

random.shuffle(newsJSON) # shuffle the list to get a random article for testing

print(f'Found {str(len(newsJSON))} stories')

for story in newsJSON:
    print(f"\nTitle: {story['title']} \nDate: {str(story['published date'])} \nDescription: {story['description']}")
    print("\n")
    #print(f"URL: {story['url']}")

    # Adding in try except block to handle errors from URL grabbing

    try:
        # decode the URL to get the actual article
        decodedURL = gnewsdecoder(story['url'], 5)
        article = Article(decodedURL["decoded_url"])
        article.download()
        article.parse()

        #print(f"Article: {article.title}")
        #print(f"Article text: {article.text}")

        messages = [
            {"role": "system", "content": historyContext},
            {"role": "system", "content": modelContext},
            {"role": "user", "content": f"Analyze the following article: {article.title} /n {article.text}"},
            ]

        response: ChatResponse = chat(model_id, messages)

        #print(response.message.content)

        decision = json.loads(response.message.content)
        #print(decision)

        # check if the decision is an incident and unique
        if decision['isIncident'] == True and decision['isUnique'] == True:
            #print("Incident detected with high confidence")

            # get the location of the incident
            location = geolocator.geocode(decision['location'])

            # make the JSON object representing the incident
            incident = {
                "title": story['title'],
                "summery": story['description'],
                "date": story['published date'],
                "url": decodedURL["decoded_url"],
                "latitude": location.latitude,
                "longitude": location.longitude
            }

            # use the timestamp as the file name for the incident
            filePath = f"./incidents/{str(time.time())}.json"

            # write the incident to a file
            with open(filePath, "w") as file:
                json.dump(incident, file)

            # add the incident to the history context
            historyContext += f"Title: {story['title']}, Date: {story['published date']}, Summery: {story['description']} \n"

            print(f"Incident detected at {location.latitude}, {location.longitude}")

        else:
            #print(f"Title: {str(article.title)}")
            print("No incident detected")
    except KeyboardInterrupt:
        print("Keyboard interrupt detected, exiting")
        break
    except:
        print("Error processing URL, could be timeout or other issue")