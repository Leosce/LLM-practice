#!/usr/bin/env python
# coding: utf-8

# In[1]:


import transformers
from transformers import T5Tokenizer, T5ForConditionalGeneration, pipeline
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
tokenizer = T5Tokenizer.from_pretrained("t5-base")
model = T5ForConditionalGeneration.from_pretrained("t5-base")


# In[2]:


classifier = pipeline("text-classification" , model = 'distilbert-base-uncased-finetuned-sst-2-english' )
summarizer = pipeline("summarization"  , model  = "sshleifer/distilbart-cnn-12-6")
ner_tagger = pipeline("ner",model = "dbmdz/bert-large-cased-finetuned-conll03-english" ,aggregation_strategy="simple" )
reader = pipeline("question-answering" ,  model = "distilbert-base-cased-distilled-squad" )
generator = pipeline('text-generation', model='gpt2-medium')
unmasker = pipeline("fill-mask", model="bert-base-uncased", framework="pt", device=-1)


# In[3]:


def classify(text):
    outputs = classifier(text)
    return outputs


# In[4]:


def summarize(text):
    outputs = summarizer(text, max_length=75, clean_up_tokenization_spaces=True)
    return outputs[0]['summary_text']


# In[5]:


def tag(text):
    outputs = ner_tagger(text)
    formatted_outputs = []
    for output in outputs:
        formatted_outputs.append(f"{output['entity_group']}, score: {output['score']}, word: {output['word']}, start: {output['start']}, end: {output['end']}")
    return formatted_outputs


# In[6]:


def read(text, lookup):
    output = reader(question=lookup, context=text)
    return f"{output['answer']}, score: {output['score']}, start: {output['start']}, end: {output['end']}"
    



# In[7]:


def generate(prompt):    
    outputs = generator(prompt, max_length=100)
    return outputs[0]['generated_text']


# In[8]:


def translate(text, language):
    sentences = sent_tokenize(text)
    translated_chunks = []

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence.endswith("."):
            sentence += "."  # Add a period if it's missing
        prompt = f"translate English to {language.capitalize()}: {sentence}"
        input_ids = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True).input_ids
        output_ids = model.generate(input_ids, max_length=512)
        translated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        translated_chunks.append(translated_text)

    full_translation = " ".join(translated_chunks)
    return full_translation


# In[9]:


def unmask(text):
    predictions = unmasker(text)
    formatted = []
    for pred in predictions:
        formatted.append(f"{pred['token_str']} (score: {pred['score']:.4f})")
    return formatted

