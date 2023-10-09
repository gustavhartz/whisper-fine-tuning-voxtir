# Voxtir finetuning of Whipser Models
This is a sample repository of how you can use your data from a Voxtir app deployment to finetune a Whisper Transformer model using Hugging Face. It's used for fine-tuning a HF model based on all the document in a Project

### Important information
* Don't try to fine-tune a model based on the baseline transcriptions created by Voxtir. This is just finetuning a model on it's own predictions. This is only usefull for wasting compute...
* This is POC code and the API might have changed since, so please refer to the [Voxtir repo](https://github.com/voxtir/voxtir) for the latest API specs
* Ensure you have permission to use the data for fine-tuning. Most transcriptions have multiple people in them. Make sure everyone agrees on the data usage


## How to use it
* Run the preprocess data
* Run the main

