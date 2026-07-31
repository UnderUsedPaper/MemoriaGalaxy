# Memoria Galaxy

Memoria Galaxy is an AI-powered journaling application that creates planets based on the user's input. This allows individuals to log down memories or experiences that they had throughout their day, making a galaxy of thoughts that the user would like to remember.

## How it works
The user puts in an input on the side bar that describes a memory or experience that they had. Based on this input, a local Ollama AI gets that input and chooses from a list of features and characteristics to give that planet. After that, the planet is created from those traits and given an AI-generated name that shows the theme and emotion from the memory given.

## Features
- Console to input memories or experiences
- Galaxy display with clickable planets
- Memory Journey which goes through each planet while playing music
- Planet fusion which combines two planets, making a combined memory
- Dashboard that shows the overall statisitcs of the user's galaxy
- Downloadable galaxies
- Filtered searching for specific plants

## Possible Future Improvements
- More characterisitcs/traits
- Fully AI generated planet designs
- More music variety
- Easier search for planets

## How to Run
pip install ollama
pip install streamlit
ollama pull qwen3:8b (or any ollama model)
py -m streamlit run app.py
