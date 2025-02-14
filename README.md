# droneReporter

This is a simple news analyzer that can be used to pull and analyze google news stories based on user-defined terms.  It then runs those articles through an LLM to determine if it meets the context the user was looking for, and then returns those articles as JSON objects.

## Installation

 Needs python versions of:
 - Ollama
 - gnews
 - newspaper3k
 - googlenewsdecoder
 - geopy
 - yaml

## Customization

Modify the [context.yaml](./configs/context.yaml) file to change the search terms and context you want the system to search for.
