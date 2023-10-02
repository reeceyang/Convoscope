import os

# OpenAI imports
import openai
openai.api_key = os.environ['OPENAI_API_KEY']

### For use with Azure OpenAI ###
useAzure = os.getenv("AZURE_OPENAI_ENDPOINT")
if useAzure:
    print("$$$ USING AZURE OPENAI $$$")
    openai.api_key = os.getenv("AZURE_OPENAI_KEY")
    openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT") # your endpoint should look like the following https://YOUR_RESOURCE_NAME.openai.azure.com/
    openai.api_type = 'azure'
    openai.api_version = '2023-05-15' # this may change in the future
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT") #This will correspond to the custom name you chose for your deployment when you deployed a model. 

ogPromptNoContext = """Please summarize the following "entity description" text to 8 words or less, extracting the most important information about the entity. The summary should be easy to parse very quickly. Leave out filler words. Don't write the name of the entity. Use less than 8 words for the entire summary. Be concise, brief, and succinct.

            Example:
            [INPUT]
            "George Washington (February 22, 1732 – December 14, 1799) was an American military officer, statesman, and Founding Father who served as the first president of the United States from 1789 to 1797."

            [OUTPUT]
            First American president, military officer, Founding Father.

            Example:
            [INPUT]
            "ChatGPT is an artificial intelligence chatbot developed by OpenAI and released in November 2022. It is built on top of OpenAI's GPT-3.5 and GPT-4 families of large language models and has been fine-tuned using both supervised and reinforcement learning techniques."
            [OUTPUT]
            AI chatbot using GPT models.

            \n Text to summarize: \n{} \nSummary (8 words or less): """

ogPromptWithContext = """
    Summarize the following "entity description" text in relation to the given "context" which is a transcript from a conversation. 
Extract only the most important information about the entitiy, as summaries must be 8 words or less. 
The summary should be easy to parse very quickly. Leave out filler words. Don't write the name of the entity. 
Use less than 8 words for the entire summary. Be concise, brief, and succinct.

Example:
[INPUT]
Text to summarize:
"LinkedIn is a business and employment-focused social media platform that works through websites and mobile apps. It was launched on May 5, 2003."

Context:
"LinkedIn was bought by Microsoft."

[OUTPUT]
Social media platform, bought by Microsoft in 2016.

Example:
[INPUT]
Text to summarize:
"Barack Hussein Obama II is an American politician who served as the 44th president of the United States from 2009 to 2017. A member of the Democratic Party, he was the first African-American president."

Context:
"Obama grew up in Chicago"

[OUTPUT]
44th US President, elected 2009, from Chicago Illinois.

\nText to summarize:\n\n
{}\n
Context:\n\n
{}\n
\nSummary (8 words or less): 
"""

class Summarizer:

    def __init__(self, databaseHandler):
        self.databaseHandler = databaseHandler

    def summarize_entity(self, entity_description: str, context: str = "", chars_to_use=1250):
        # shorten entity_description if too long
        entity_description = entity_description[:min(
            chars_to_use, len(entity_description))]

        # Check cache for summary first
        cache_key = entity_description + ' c: ' + context
        summary = self.databaseHandler.findCachedSummary(cache_key)
        if summary: 
            print("$$$ SUMMARY: FOUND CACHED SUMMARY")
            return summary
        
        # Summary does not exist. Get it with OpenAI
        print("$$$ SUMMARY: SUMMARIZING WITH OPENAI")
        summary = self.summarize_entity_with_openai(entity_description, context)
        self.databaseHandler.saveCachedSummary(cache_key, summary)
        return summary

    def summarize_entity_with_openai(self, entity_description: str, context: str = ""):
            if context and context != "":
                prompt = ogPromptWithContext.format(entity_description, context)
            else:
                prompt = ogPromptNoContext.format(entity_description)
            
            if useAzure:
                chat_completion = openai.Completion.create(engine=deployment_name, prompt=prompt, temperature=0.5, max_tokens=20)
            else:
                chat_completion = openai.Completion.create(model="text-davinci-002", prompt=prompt, temperature=0.5, max_tokens=20)
                
            response = chat_completion.choices[0].text
            return response